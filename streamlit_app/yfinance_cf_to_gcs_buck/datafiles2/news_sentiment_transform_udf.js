function transform(line) {
    var values = line.split(',');
    var obj = new Object();
    obj.Company = values[0];
    obj.Date = values[1];
    obj.News = values[2];
    obj.Sentiment = values[3];
    obj.Positive = values[4];
    obj.Negative = values[5];
    obj.Neutral = values[6];
    var jsonString = JSON.stringify(obj);
    return jsonString;
    }
