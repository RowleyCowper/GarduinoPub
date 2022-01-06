# Garduino - The Garden Project

<h2> Overview </h2>
This is a simple project to automatically water plants, logging the data to a secondary device that would then publish the results to a database in AWS.  As a terrible green thumb, I wanted a way to improve my gardening, whilst learning some new skills and gain some actionable data that I could use to analyse for trends and tune the watering functions.

It comprised of:
* using the Sparkfun Arduino Redboard, which logged moisture and light, and controlled the water pump (Garduino.ino)
* using a Beaglebone black as a secondary device to log the results to via serial as a CSV (GarduinoBase.py)
* using a Beaglebone black to publish the results to a database on AWS via the aws-iot-device-sdk-python to avoid data loss and permit further analysis (GarduinoAWS.py)

In the end the Arduino watering tool worked, as did the local monitoring.  The data was published to AWS, but it was at a very early stage and so the published data wasn't yet useful.  At this point, I put my plants outside, and a squirrel ate them all in one night.  Bugger.  Thus I shelved this project, and moved onto the next one, which was to build a squirrel-proof cage over the garden patch.  So far, I'm beating the squirrels this time!

<table>
<tr>
<th>
<img src="https://github.com/RowleyCowper/GarduinoPub/blob/main/references/gard.png" width=300>
</th>
<th>
<img src="https://github.com/RowleyCowper/GarduinoPub/blob/main/references/inst.jpeg?raw=true" width=300>
</th>
</tr>
</table>

<h2> HW Reference </h2>
* The wiring diagram can be found in <a href="https://github.com/RowleyCowper/GarduinoPub/blob/main/references/WayInTop.pdf"> the included PDF</a>. I used the <a href="https://www.amazon.com/gp/product/B07TMVNTDK/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1">WayInTop kit available on Amazon.</a>
* As a control, I used a manual moisture and light sensor, also found on <a href="https://www.amazon.com/gp/product/B07BR52P26/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1">Amazon</a>.
