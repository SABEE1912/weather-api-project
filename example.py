import mysql.connector
import requests
import json
import re
import logging
from dotenv import load_dotenv
import os
load_dotenv()
logging.basicConfig(filename="validation.log",level=logging.INFO,format="%(asctime)s  %(levelname)s  %(message)s")
from datetime import datetime
conn=mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
print("connection established successfully")
failed_validations=0
cursor=conn.cursor()
cursor.execute("""
               create table if not exists weather_reports(
               id int primary key auto_increment,
               city varchar(50),country varchar(50),
               temperature Decimal(5,2),humidity int,
               wind_speed Decimal(5,2),weather_condition varchar(50),
               search_date DATE,search_time TIME)
               """)
print("table created successfully")
def validation_log(city,status):
    now=datetime.now()
    with open("validatin.txt","a") as file:
        file.write(f"{now.strftime('%d-%m-%Y  %H:%M   %p')}\n"   )
        file.write(f"{city}\n")
        file.write(f"{status}\n")
        file.write("-" * 30 +  "\n")
def check_weather():
    global failed_validations
    validation_status = "FAILED"
    city=input("enter city:")
    api_key=os.getenv("API_KEY")
    url=f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response=requests.get(url)
    data=response.json()
    raw_response=json.dumps(data)
    city_name=data["location"]["name"]
    if(validate_city(city_name)):
        print("valid city name")
    else:
        print("invalid city name")
        return
    country=data["location"]["country"]
    if(validate_country(country)):
        print("valid country name")
    else:
        print("invalid country name")
        return
    temperature=data["current"]["temp_c"]
    if(validate_temperature(temperature)):
        print("valid temperature")
    else:
        print("invalid temperature")
        return
    humidity=data["current"]["humidity"]
    if(validate_humidity(humidity)):
        print("valid humidity")
    else:
        print("invalid humidity")
        return
    wind_speed=data["current"]["wind_kph"]
    if(validate_wind_speed(wind_speed)):
        print("valid wind speed")
    else:
        print("invalid wind speed")
        return
    condition=data["current"]["condition"]["text"]
    if(validate_condition(condition)):
        print("valid condition")
    else:
        print("invalid condition")
        return
    valid_city=validate_city(city_name)
    valid_country=validate_country(country)
    valid_temperature=validate_temperature(temperature)
    valid_humidity=validate_humidity(humidity)
    valid_wind_speed=validate_wind_speed(wind_speed)
    valid_condition=validate_condition(condition)
    print("CITY VALIDATION        :", "PASSED" if valid_city else "FAILED")
    print("COUNTRY VALIDATION     :", "PASSED" if valid_country else "FAILED")
    print("TEMPERATURE VALIDATION :", "PASSED" if valid_temperature else "FAILED")
    print("HUMIDITY VALIDATION    :", "PASSED" if valid_humidity else "FAILED")
    print("WIND SPEED VALIDATION  :", "PASSED" if valid_wind_speed else "FAILED")
    print("CONDITION VALIDATION   :", "PASSED" if valid_condition else "FAILED")
    validation_log(city_name,"PASSED")

    if (valid_city and valid_country and valid_temperature and valid_humidity and valid_wind_speed and valid_condition):
        print("All validations passed")
        validation_status = "PASSED"
        logging.info(f"City={city_name},Country={country},"
                     f"Temperature={temperature},Humidity={humidity},"
                     f"Wind_speed={wind_speed},Condition={condition},"
                     f"Status=PASSED")
        print("-" * 32)
        print("Weather Report")
        print("-" * 32)

        print(f"City        : {city_name}")
        print(f"Country     : {country}")
        print(f"Temperature : {temperature}°C")
        print(f"Humidity    : {humidity}%")
        print(f"Wind Speed  : {wind_speed} km/h")
        print(f"Condition   : {condition}")
    else:
        failed_validations+=1
        print("VALIDATION FAILED")
        print("RECORD NOT SAVED")
        logging.error(
        f"City={city_name}, Country={country}, "
        f"Status=FAILED")
        export_invalid_record(city_name,country,temperature,humidity,wind_speed,condition)
        return
    now=datetime.now()
    search_date=now.date()
    search_time=now.time()
    cursor.execute("""insert into weather_reports(
            city,country,temperature,humidity,wind_speed,
               weather_condition,search_date,search_time,raw_response,validation_status)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
               (city_name,country,temperature,humidity,
               wind_speed,condition,search_date,search_time,raw_response,validation_status
               ))
    conn.commit()   
    print("weather data inserted successfully")

def validate_city(city):
    if re.fullmatch(r"[a-zA-Z .]+",city):
        return True
    else:
        return False

def validate_country(countr):
    if re.fullmatch(r"[a-zA-Z ]+",countr):
        return True
    else:
        return False

def validate_temperature(temp):
    if re.fullmatch(r"-?\d+(\.\d+)",str(temp)):
        return True
    else:
        return False

def validate_wind_speed(windspeed):
    if re.fullmatch(r"-?\d+(\.\d+)",str(windspeed)):
        return True
    else:
        return False
def validate_humidity(humid):
    if re.fullmatch(r"\d+",str(humid)):
        return True
    else:
        return False
    
def validate_condition(con):
    if re.fullmatch(r"[a-zA-Z ]+",con):
        return True
    else:
        return False


def view_history():
    cursor.execute("select * from weather_reports")
    records=cursor.fetchall()
    for row in records:
        print(row)

def last_weather_search():
    cursor.execute("select * from weather_reports order by id desc limit 1")
    record=cursor.fetchone()
    if record:
        print("*" * 30)
        print("city:",record[1])
        print("country:",record[2])
        print("temperature:",record[3])
        print("humidity:",record[4])
        print("wind speed:",record[5])
        print("condition:",record[6])
        print("search date:",record[7])
        print("search time:",record[8])
    else:
        print("no record found on the given city")
def hottest_city():
    cursor.execute("select * from weather_reports order by temperature desc limit 1;")
    hottest_city = cursor.fetchone()
    print(hottest_city)

def coldest_city():
    cursor.execute("select * from weather_reports order by temperature  limit 1;")
    hottest_city = cursor.fetchone()
    print(hottest_city)

def count_weather_searches():
    cursor.execute("select count(*) from weather_reports;")
    cities_count=cursor.fetchone()
    print(cities_count)

def delete_weather():
    delete_city=input("enter the city that you want to delete:")
    cursor.execute("delete from weather_reports where city=%s",(delete_city,))
    conn.commit()
    if cursor.rowcount>0:
        print("city deleted successfully")
    else:
        print("city you entered  not found")


def export_weather():
    with open("weather_history.txt","a") as f:
        cursor.execute("select * from weather_reports;")
        records=cursor.fetchall()
        for row in records:
            f.write(str(row) +"\n")
    print("weather exported successfully!")

def save_API_response():
    cursor.execute("""
                select raw_response from weather_reports order by id desc limit 1
                   """   )
    record=cursor.fetchone()
    if(record):
        print(record[0])
    else:
        print("No API response found")

def count_failed_validation():
    print("Total Failed Validations: ",failed_validations)

def export_invalid_record(city_name,country,temperature,humidity,wind_speed,condition):
    now = datetime.now()
    with open("INVALID_WEATHER_RECORDS.txt","a") as f:
        f.write(f"Date : {now.date()}\n")
        f.write(f"Time : {now.strftime('%H:%M:%S')}\n")
        f.write(f"City : {city_name}\n")
        f.write(f"Country : {country}\n")
        f.write(f"Temperature : {temperature}\n")
        f.write(f"Humidity : {humidity}\n")
        f.write(f"Wind Speed : {wind_speed}\n")
        f.write(f"Condition : {condition}\n")
        f.write("Validation Status : FAILED\n")
        f.write("-" * 40 + "\n")
while True:
    print("1.check weather")
    print("2.view weather history")
    print("3.view last weather search")
    print("4.check the hottest city ")
    print("5.check the coldest city")
    print("6.count of weather searches")
    print("7.delete weather history")
    print("8.export weather history")
    print("9.save API response")
    print("10.Count failed validations")
    print("11.exit:")
    ch=int(input("enter your choice:"))
    if(ch==1):
        check_weather()
    elif(ch==2):
        view_history()
    elif(ch==3):
        last_weather_search()
    elif(ch==4):
        hottest_city()
    elif(ch==5):
        coldest_city()
    elif(ch==6):
        count_weather_searches()
    elif(ch==7):
        delete_weather()
    elif(ch==8):
        export_weather()
    elif(ch==9):
        save_API_response()
    elif(ch==10):
        count_failed_validation()
    else:
        print("exiting the program....")
        break

