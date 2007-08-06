#!/usr/bin/env python


import time



def write_starting_content(handle):
    handle.write('<h1>Pylot - Web Performance Results</h1>\n')


def write_paragraph(handle, txt):
    handle.write('<p>%s</p>\n' % txt)
    
    
def write_images(handle):
    handle.write('<h2>Response Time</h2>\n')
    handle.write('<img src="response_time_graph.png" alt="response time graph">\n')
    handle.write('<h2>Throughput</h2>\n')
    handle.write('<img src="throughput_graph.png" alt="throughput graph">\n')

    
def write_stats_tables(handle, stats_dict):
    handle.write('<p><br /></p>')
    handle.write('<table>\n')
    handle.write('<th>Response Time (secs)</th><th>Throughput (req/sec)</th>\n')
    handle.write('<tr>\n')
    handle.write('<td>\n')   
    handle.write('<table>\n')
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('avg', stats_dict['response_avg']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('stdev', stats_dict['response_stdev']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('min', stats_dict['response_min']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('max', stats_dict['response_max']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('50th %', stats_dict['response_50pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('80th %', stats_dict['response_80pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('90th %', stats_dict['response_90pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('95th %', stats_dict['response_95pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('99th %', stats_dict['response_99pct']))
    handle.write('</table>\n')
    handle.write('</td>\n')
    handle.write('<td>\n')
    handle.write('<table>\n')
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('avg', stats_dict['throughput_avg']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('stdev', stats_dict['throughput_stdev']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('min', stats_dict['throughput_min']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('max', stats_dict['throughput_max']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('50th %', stats_dict['throughput_50pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('80th %', stats_dict['throughput_80pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('90th %', stats_dict['throughput_90pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('95th %', stats_dict['throughput_95pct']))
    handle.write('<tr><td>%s</td><td>%.2f</td></tr>\n' % ('99th %', stats_dict['throughput_99pct']))
    handle.write('</table>\n')
    handle.write('</td>\n')
    handle.write('</tr>\n')
    handle.write('</table>\n')


def write_summary_results(handle, summary_dict):
    handle.write('<b>%s:</b> &nbsp;%s<br />\n' % ('report generated', summary_dict['cur_time']))
    handle.write('<b>%s:</b> &nbsp;%s<br />\n' % ('test start', summary_dict['start_time']))
    handle.write('<b>%s:</b> &nbsp;%s<br />\n' % ('test finish', summary_dict['end_time']))
    handle.write('<h2>Summary</h2>')
    handle.write('<table>\n')
    handle.write('<tr><td>%s</td><td>%d</td></tr>\n' % ('test duration (secs)', summary_dict['duration']))
    handle.write('<tr><td>%s</td><td>%d</td></tr>\n' % ('agents', summary_dict['num_agents']))
    handle.write('<tr><td>%s</td><td>%d</td></tr>\n' % ('requests', summary_dict['req_count']))
    handle.write('<tr><td>%s</td><td>%d</td></tr>\n' % ('errors', summary_dict['err_count']))
    handle.write('<tr><td>%s</td><td>%d</td></tr>\n' % ('data received (bytes)', summary_dict['bytes_received']))
    handle.write('</table>\n')
    

def write_head_html(handle):
    handle.write("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>Pylot - Results</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <meta http-equiv="Content-Language" content="en" />
    <style type="text/css">
        body {
            background-color: #FFFFFF;
            color: #000000;
            font-family: Trebuchet MS, Verdana, sans-serif;
            font-size: 11px;
            padding: 10px;
        }
        h1 {
            font-size: 16px;
            margin-bottom: 0.5em;
            background: #FF9933;
            padding-left: 5px;
            padding-top: 2px;
        }
        h2 {
            font-size: 12px;
            background: #C0C0C0;
            padding-left: 5px;
            margin-top: 2em;
            margin-bottom: .75em;
        }
        h3 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        h4 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        p {
            margin: 0;
            padding: 0;
        }
        table {
            margin-bottom: 0;
        }
        td {
            text-align: right;
            color: #000000;
            background: #FFFFFF;
            padding-left: 10px;
            padding-bottom: 0px;
        }
        th {
            text-align: center;
            font-size: 12px;
            padding-right: 30px;
            padding-left: 30px;
            color: #000000;
            background: #C0C0C0;
        }
    </style>
</head>
<body>
""")
  

def write_closing_html(handle):
    handle.write("""\
</body>
</html>
    """)




