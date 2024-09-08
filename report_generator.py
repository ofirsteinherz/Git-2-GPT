import os
from html import escape

def create_html_report(html_file, file_list, total_tokens, total_cost):
    print(f"Creating HTML report: {html_file}")
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
        html.write("<tr><th>Folder Path</th><th>File Name</th><th>Tokens</th><th>Cost</th><th>Link</th></tr>")

        # Variable to track the current folder and its background color
        prev_folder_path = None
        background_color_toggle = False  # Toggle between white and light gray for folders
        folder_background_color = "white"  # Start with white for the first folder

        # Folder background color to alternate between
        light_gray = "#f2f2f2"
        
        # Create rows for each file
        for parts, tokens, cost, file_path in file_list:
            # Extract the folder path and file name
            if len(parts[:-1]) > 0:
                folder_path = escape(os.path.join(*parts[:-1]))  # Join all parts except the last one (file name)
            else:
                folder_path = "/"  # Treat files without a folder as being in the root folder "/"

            file_name = escape(parts[-1])  # Last part is the file name

            cost_info = f"${float(cost):.10f}"  # Formatting cost for clarity
            link = f"<a href='file:///{escape(os.path.abspath(file_path))}'>link</a>"

            # Check if the folder path is the same as the previous row's folder path
            if folder_path != prev_folder_path:
                # Toggle the folder background color
                background_color_toggle = not background_color_toggle
                folder_background_color = "white" if background_color_toggle else light_gray
                prev_folder_path = folder_path

            # Write folder path with alternating background color (only this column is affected)
            html.write(f"<td style='background-color:{folder_background_color};'>{folder_path}</td>")
            # Write file name, tokens, cost, and link (all of which should have white background)
            html.write(f"<td style='background-color:white;'>{file_name}</td>")
            html.write(f"<td style='background-color:white;'>{tokens}</td>")
            html.write(f"<td style='background-color:white;'>{cost_info}</td>")
            html.write(f"<td style='background-color:white;'>{link}</td>")
            html.write("</tr>")

        html.write("</table></section></body></html>")
    print(f"HTML report created successfully.")
