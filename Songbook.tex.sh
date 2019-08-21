#!/usr/bin/env bash


cat <<EOF
\documentclass{book}

\providecommand{\bookname}{Songbook}

\input{Misc/basic}

% different spacing
\versesep=10pt plus 2pt minus 4pt
\afterpreludeskip=2pt
\beforepostludeskip=2pt

\newindex{Seitenzahlen}{Songbook}
\indexsongsas{Seitenzahlen}{\thepage}

\begin{document}
\begin{songs}{Seitenzahlen}

\showindex[2]{Inhaltsverzeichnis}{Seitenzahlen}

EOF

for file in Lieder/*.tex; 
    do echo "\\input{$file}"
done

cat <<EOF

\end{songs}
\end{document}
EOF
