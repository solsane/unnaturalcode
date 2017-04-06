from __future__ import print_function, division

import csv
import sys
import os
import os.path

def inc(d, k):
  if k not in d:
      d[k] = 0
  d[k] += 1
    
acc_tab = {}

for arg in sys.argv[1:]:
    with open(arg, 'rb') as csvfile:
        csvr = csv.reader(csvfile)
        for stuff in csvr:
            #print(stuff, file=sys.stderr)
            (path,
            mutation,
            window_rank,
            window_entropy,
            token_type,
            token_line,
            token_string,
            parse_error,
            parse_error_same_line,
            parse_error_file_name,
            parse_error_line,
            parse_error_function,
            window_start_line,
            token_start_line,
            line_rank,
            token_rank,
            fix_notruevalid,
            fix_valid,
            fix_operation) = stuff
            if mutation not in acc_tab:
                acc_tab[mutation] = {
                }
            mut_tab = acc_tab[mutation]
            inc(mut_tab, 'total')
            inc(mut_tab, fix_operation)
            inc(mut_tab, fix_notruevalid)
            if fix_notruevalid == 'TrueFix':
                inc(mut_tab, 'ValidFix')
        
rows = [
  ('insertRandom', 'Insertion'),
  ('deleteRandom', 'Deletion'),        
  ('replaceRandom', 'Substitution'),        
]

cols = [
  'Insert',
  'Delete',
  'Replace',
  'NoFix',
  'ValidFix',
  'TrueFix'
]

hilite = set([
  ('insertRandom', 'Delete'),
  ('deleteRandom', 'Insert'),        
  ('replaceRandom', 'Replace'),        
  ])

print(r"""
% Requires this in the preamble:
%
%  \usepackage(xcolor,colortbl}
%  \definecolor{highlightcolor}{rgb}{0.8,0.8,0.8}
%  \newcommand{\highlight}[1]{\cellcolor{highlightcolor} #1}
%
\begin{tabular}{@{}lrrrrrrrrrrrr@{}}
\toprule
             &                          \multicolumn{6}{c}{Fix created by 10-gram model}                               &                               \multicolumn{6}{c}{Summary}                                 \\
\cmidrule(r){2-7} \cmidrule{8-13}
             & \multicolumn{2}{c}{Insertion} & \multicolumn{2}{c}{Deletion} & \multicolumn{2}{c}{Substitution} & \multicolumn{2}{c}{No fix} & \multicolumn{2}{c}{Valid fix} & \multicolumn{2}{c}{True fix} \\
 Mutation    & Total        & \%             & Total        & \%            & Total          & \%              & Total        & \%          & Total          & \%           & Total        & \%            \\
\cmidrule(r){2-7} \cmidrule{8-13}
""".strip())
# Print each row (mutation) in the table
for row, name in rows:
    rowdata = [name]
    for col in cols:
        t = ""
        if (row, col) in hilite:
          t += "\\highlight{"
        t += str(acc_tab[row][col])
        if (row, col) in hilite:
          t += "}"
        rowdata.append(t)
        t = ""
        if (row, col) in hilite:
          t += "\\highlight{"
        t += "%.2f\\%%" % ((acc_tab[row][col]/acc_tab[row]['total'])*100.0,)
        if (row, col) in hilite:
          t += "}"
        rowdata.append(t)
    print(" & ".join(rowdata) + r"\\")

print(r"""
\bottomrule
\end{tabular}
""".strip())
