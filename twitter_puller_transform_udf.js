function transform(line) {
    var values = line.split(',');
    var obj = new Object();
    obj.Company = values[0];
    obj.Id = values[1];
    obj.Date = values[2];
    obj.Text = values[3];
    obj.Negative = values[4];
    obj.Neutral = values[5];
    obj.Positive = values[6];
    obj.Compound = values[7];
    var jsonString = JSON.stringify(obj);
    return jsonString;
}