wait-n ()
{ StartJobs="$(jobs -p)"
  CurJobs="$(jobs -p)"
  while diff -q  <(echo -e "$StartJobs") <(echo -e "$CurJobs") >/dev/null
  do
    sleep 1
    CurJobs="$(jobs -p)"
  done
}