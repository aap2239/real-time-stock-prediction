function transform(line) {
    var values = line.split(',');
    var obj = new Object();
    obj.Date = values[0];
    obj.Open = values[1];
    obj.High = values[2];
    obj.Low = values[3];
    obj.Close = values[4];
    obj.AdjClose = values[5];
    obj.Volume = values[6];
    obj.Company = values[7];
    var jsonString = JSON.stringify(obj);
    return jsonString;
}
