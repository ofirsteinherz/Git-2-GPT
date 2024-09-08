import os
from html import escape

def create_html_report(html_file, file_list, max_depth, total_tokens, total_cost):
    with open(html_file, 'w') as html:
        html.write("<html><head><style>")
        html.write("body {font-family: Arial, sans-serif;}")
        html.write("table {border-collapse: collapse; margin-left: auto; margin-right: auto;}")
        html.write("th, td {border: 1px solid black; padding: 8px; text-align: left;}")
        html.write("th {background-color: #f2f2f2;}")
        html.write("section {display: flex; justify-content: center;}")
        html.write("table {max-width: 80%; width: 100%;}")
        html.write("</style></head><body>")
        html.write("<h1 style='text-align:center;'>File Report</h1>")
        html.write(f"<p style='text-align:center;'>Total Tokens: {total_tokens}</p>")
        html.write(f"<p style='text-align:center;'>Total Cost: ${float(total_cost):.10f}</p>")
        html.write("<section><table>")
        html.write("<tr>")
        
        for i in range(max_depth):
            html.write(f"<th>Folder {i+1}</th>")
        html.write("<th>File Name</th><th>Tokens</th><th>Cost</th><th>Link</th></tr>")
        
        for parts, tokens, cost, file_path in file_list:
            html.write("<tr>")
            depth = len(parts) - 1
            for i in range(max_depth):
                if i < depth:
                    html.write(f"<td>{escape(parts[i])}</td>")
                elif i == depth:
                    html.write(f"<td>{escape(parts[i])}</td>")
                else:
                    html.write(f"<td></td>")

            file_name = escape(parts[-1])
            cost_info = f"${float(cost):.10f}"
            link = f"<a href='file:///{escape(os.path.abspath(file_path))}'>link</a>"
            html.write(f"<td>{file_name}</td><td>{tokens}</td><td>{cost_info}</td><td>{link}</td>")
            html.write("</tr>")
        
        html.write("</table></section></body></html>")
