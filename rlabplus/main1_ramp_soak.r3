//
//
//
EOL = "\r";
temp_start = 30;
temp_end = 60;
temp_rate = 1; // deg/minute
temp_delta = 1; // increase in temperature for sp1

time_soak = 30; // min

url = "tcp://1.2.3.4:51234";
open(url);

// set sp1 to temp_start
"Setting "+num2str(temp_start,"sp1=%.1f") ?
writem(url,num2str(temp_start,"sp1=%.1f\r"));
do
{
  resp = readm(url);
}
while (strindex(resp,"OK")<1);

readm(url);
writem(url,"sp1" + EOL);
do
{
  spinner();
  temp_sp1 = readm(url);
}
while (isempty(temp_sp1));
temp_sp1 = strtod(temp_sp1);
" Done\n" ?

// wait till sp1 reaches start temperature
readm (url);
"Waiting to start:" ?
do
{
  sleep(5);
  smiley();
  writem(url,"val" + EOL);
  do
  {
    s_temp = readm(url);
  }
  while (isempty(s_temp));
  temp = strtod(s_temp);
}
while (abs(temp - temp_start)>0.5);
" Done\n" ?

// now start to ramp up at 'temp_delta' Deg increments
readm (url);
"Ramping started:" ?
temp = temp_start;
dt = temp_delta ./ temp_rate;
Ns = ceil((temp_end - temp_start) / temp_delta); // this many steps
tic();
for (i in 1:Ns)
{
  temp = temp + temp_delta;

  // set sp1
  writem(url,num2str(temp,"sp1=%.1f\r"));
  do
  {
    resp = readm(url);
  }
  while (strindex(resp,"OK")<1);

  // wait
  while(toc()<i*dt*60)
  {
    spinner();
    sleep(1);
  }
}
" Completed!\n" ?

// soak, then go to room temperature
"Soaking: " ?
for (i in 1:time_soak)
{
  spinner();
  sleep(60);
}
" Completed!\n" ?

writem(url,"sp1=22\r");
do
{
  resp = readm(url);
}
while (strindex(resp,"OK")<1);
writem(url,"quit\r");
close(url);
"Connection closed and disconnect completed!\n" ?

