import json
import os

files = [ "CSS326-24G-2S+__2.18_763906357EDB.json","CRS312-4C+8XG_r2_2.18_HE208JZZ6YZ.json","CRS328-24P-4S+_r2_2.18_HJE0A2EJNXH.json"]
files = os.listdir("samples")
files = [f for f in files if os.path.isfile('samples/'+f)]

# field, api,webpage,webfield,decode
# print to .markdown
import csv

class Table:
    def __init__(self, name):
        self.about = name
        self.column_headers = []
        self.rows = {}

    def add_column(self, column_name):
        if column_name not in self.column_headers:
            self.column_headers.append(column_name)
            for row in self.rows:
                self.rows[row].append(["?"])

    def add_row(self, row_name):
        if row_name not in self.rows:
            self.rows[row_name] = ["?"] * len(self.column_headers)

    def set_value(self, column, row, value):
        self.add_row(row)
        self.add_column(column)
        columnnr = self.column_headers.index(column)
        self.rows[row][columnnr] = value

    def print(self):
        def print_array(what, array):
            line = what
            komma = ","
            for item in array:
                line += komma + item
                komma = ","
            print(line)
        print_array(self.about, self.column_headers)
        for row in sorted(self.rows.keys()):
            print_array(row,self.rows[row])
        print("")

    def print_html(self,fp):
        def print_array(what, array, ttype):
            line = "<tr><{ttype}>{what}</{ttype}>".format(ttype=ttype,what=what)
            for item in array:
                line += "<{ttype}>{item}</{ttype}>".format(ttype=ttype, item=item)
            fp.write(line+"</tr>")
        fp.write("<table><caption>{about}</caption>".format(about= self.about))
        print_array("", self.column_headers,"th")
        for row in sorted(self.rows.keys()):
            print_array(row,self.rows[row],"td")
        fp.write("</table>")

    def write_markdown(self,fp):
        def print_array(what, array):
            line = "|{what}|".format(what=what)
            for item in array:
                line += "{item}|".format(item=item)
            fp.write(line+"\n")
        
        print_array(self.about, self.column_headers)
        for item in self.column_headers:
            fp.write("|---")
        fp.write("|---|\n")
        for row in sorted(self.rows.keys()):
            print_array(row,self.rows[row])
        fp.write("\n\n")
        

    def write_csv(self,csvwriter,api):
        for row in sorted(self.rows.keys()):
            csvwriter.writerow([row,api,"?","?","?"])
            
tables = {}

# read the information of every field, and put it in the table
with open('SWoS-api.csv', newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
    for row in csvreader:
        # field;api;webpage;webfield;decode
        if row["api"] not in tables:
            tables[row["api"]] = Table(row["api"])     # make sure a table for this api is there
        tables[row["api"]].add_row(row["field"])
        for i in ("webpage","webfield","decode"):
            #tables[row["api"]].add_row(row["webpage"])
            tables[row["api"]].set_value(i,row["field"],row[i])
        #tables[row["api"]].add_row(row["webfield"])
        #tables[row["api"]].add_row(row["decode"])
        
for file in files:
    with open("samples/" + file, 'r') as fp:
        data = json.load(fp)
    column = file.split("_")[0]    # type of switch eg CRS312-4C+8XG
    for api in data:
        if api.startswith("/"):
            if api not in tables:
                tables[api] = Table(api)
            if type(data[api]["data"]) == list:
                items = data[api]["data"][0]
                prefix="[]"
            else:
                items = data[api]["data"]
                prefix=""
            for sample_key in items:
                if isinstance(sample_key,str):
                    sample_value = items[sample_key]
                    if isinstance(sample_value,str):
                        tables[api].add_row(prefix + sample_key)
                        tables[api].set_value(column,prefix + sample_key, sample_value)
                    if isinstance(sample_value,list):
                        tables[api].add_row(sample_key + "[]")
                        tables[api].set_value(column, sample_key + "[]", str(len(sample_value)) + "x " + sample_value[0])

with open('SWoS-api-new.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["field","api","webpage","webfield","decode"])   # write header
    for table in tables:
        tables[table].write_csv(csvwriter, table)

with open("SWos-api.html", mode="w") as fp:
    fp.write("""<html><head><style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style></head><body>""")

    for table in tables:
        tables[table].print_html(fp)
    fp.write("</body></html>")

with open("SWos-api.md", mode="w") as fp:
    for table in tables:
        tables[table].write_markdown(fp)
