from fastapi import FastAPI, UploadFile, File, HTTPException
from scoring_logic import process_and_score
import shutil
import os
import uuid # Added to generate unique filenames

app = FastAPI()

# ⚠️ NOTICE: 'async' is removed from the line below! ⚠️
@app.post("/analyze")
def analyze_trip(sensor_csv: UploadFile = File(...), driving_csv: UploadFile = File(...)):
    # Generate unique filenames so simultaneous requests don't break
    unique_id = str(uuid.uuid4())
    sensor_path = f"temp_sensor_{unique_id}.csv"
    driving_path = f"temp_driving_{unique_id}.csv"

    try:
        with open(sensor_path, "wb") as buffer:
            shutil.copyfileobj(sensor_csv.file, buffer)
        with open(driving_path, "wb") as buffer:
            shutil.copyfileobj(driving_csv.file, buffer)

        # Calculate score using our logic
        result = process_and_score(sensor_path, driving_path)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        if os.path.exists(sensor_path): os.remove(sensor_path)
        if os.path.exists(driving_path): os.remove(driving_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)