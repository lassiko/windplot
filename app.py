from flask import Flask, Markup, render_template, request

import xml.etree.ElementTree as ET
import collections
import sys
sys.path.append('/home/site/wwwroot')
import requests
import datetime as dt

app = Flask(__name__)

@app.route('/line', methods=["GET", "POST"])
def line():
    station = request.form.get("obstat")
    print ("Station", station)
    if station == None:
        station="100996"

    weather_baga_url = "http://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::observations::weather::multipointcoverage&fmisid=" + station + "&parameters=Temperature,Humidity,DewPoint,WindSpeedMS,WindDirection,WindGust"
    data = requests.get(weather_baga_url)
    root = ET.fromstring(data.text)
    for member in root.iter('{http://www.opengis.net/wfs/2.0}member'):
        for GridSeriesObservation in member.iter('{http://inspire.ec.europa.eu/schemas/omso/3.0}GridSeriesObservation'):
            for result in GridSeriesObservation.iter('{http://www.opengis.net/om/2.0}result'):
                for MultiPointCoverage in result.iter('{http://www.opengis.net/gmlcov/1.0}MultiPointCoverage'):
                    for domainSet in MultiPointCoverage.iter('{http://www.opengis.net/gml/3.2}domainSet'):
                        for SimpleMultiPoint in domainSet.iter('{http://www.opengis.net/gmlcov/1.0}SimpleMultiPoint'):
                            for positions in SimpleMultiPoint.iter('{http://www.opengis.net/gmlcov/1.0}positions'):
                                timestamps = positions.text
                                ts2 = timestamps.split('\n')
                    for rangeSet in MultiPointCoverage.iter('{http://www.opengis.net/gml/3.2}rangeSet'):
                        for DataBlock in rangeSet.iter('{http://www.opengis.net/gml/3.2}DataBlock'):
                            for doubleOrNilReasonTupleList in DataBlock.iter('{http://www.opengis.net/gml/3.2}doubleOrNilReasonTupleList'):
                                measurements = doubleOrNilReasonTupleList.text
                                me2 = measurements.split('\n')
    ts2 = [x for x in ts2 if x != '']
    me2 = [x for x in me2 if x != '']
    observations2 = []
    for i in range (len(me2)-1):
        observation = []
        ts3 = ts2[i].split(' ')
        unixtime = int(ts3[len(ts3)-1])
        utc_time = dt.datetime.fromtimestamp(unixtime)
        local_time = utc_time.strftime("%H:%M")
        observation.append(local_time)
        me3 = me2[i].split(' ')
        me3 = [x for x in me3 if x != '']
        for j in range (len(me3)):
            observation.append(float(me3[j]))
        observations2.append(observation)
    tstamp = []
    winddir = []
    windspd = []
    windgst = []
    for t in range (len(observations2)):
        tstamp.append(observations2[t][0])
        windspd.append(observations2[t][4])
        winddir.append(observations2[t][5])
        windgst.append(observations2[t][6])
    wdmax = max(winddir)
    wdmin = min(winddir)
    if wdmax-wdmin > 180:
        for t in range (len(winddir)):
            if winddir[t] > 180:
                winddir[t] -= 360

    return render_template('line_chart.html', title='GOF wind', wmax=wdmax, wmin=wdmin, t=tstamp, s=windspd, d=winddir,g=windgst,station=station)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)