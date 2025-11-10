import json

files = [ "CRS312-4C+8XG_r2_2.18_HE208JZZ6YZ.json","CRS328-24P-4S+_r2_2.18_HJE0A2EJNXH.json"]

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

    def print_html(self):
        def print_array(what, array, ttype):
            line = "<tr><{ttype}>{what}</{ttype}>".format(ttype=ttype,what=what)
            for item in array:
                line += "<{ttype}>{item}</{ttype}>".format(ttype=ttype, item=item)
            print(line+"</tr>")
        print("<table><caption>{about}</caption>".format(about= self.about))
        print_array("", self.column_headers,"th")
        for row in sorted(self.rows.keys()):
            print_array(row,self.rows[row],"td")
        print("</table>")
        
tables = {}
for file in files:
    with open(file, 'r') as fp:
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
print("<html><body>")
for table in tables:
    tables[table].print_html()
print("</body></html>")
