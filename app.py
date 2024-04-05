from flask import Flask, request, jsonify
from flask.views import MethodView
from datetime import datetime, timedelta
from typing import Optional
import pydantic

app = Flask(__name__)
data_storage = []

class WeatherAndAirQualityData(pydantic.BaseModel):
    timestamp: datetime
    temperature: Optional[int] = pydantic.Field(None, ge=-50, le=50)
    pressure: Optional[int] = pydantic.Field(None, ge=800, le=1200)
    humidity: Optional[int] = pydantic.Field(None, ge=0, le=100)
    aqi: Optional[int] = pydantic.Field(None, ge=0)

class AirQualityRecordView(MethodView):
    def get(self):
        query_timestamp = request.args.get('timestamp', type=lambda x: datetime.fromisoformat(x))
        if not query_timestamp:
            return jsonify({"error": "Timestamp query parameter is required."}), 400
        closest_record = min(
            data_storage, 
            key=lambda x: abs(x.timestamp - query_timestamp), 
            default=None
        )
        
        if closest_record:
            return jsonify(closest_record.dict())
        else:
            return jsonify({"message": "No data found near the provided timestamp."}), 404

    def post(self):
        try:
            data = request.json
            record = WeatherAndAirQualityData(**data)
            data_storage.append(record)
            return jsonify(record.dict()), 201
        except pydantic.ValidationError as e:
            return jsonify({"error": str(e)}), 400

app.add_url_rule('/air_quality', view_func=AirQualityRecordView.as_view('air_quality_api'))

if __name__ == '__main__':
    app.run(debug=True)
