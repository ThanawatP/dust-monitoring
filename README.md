# Dust (PM2.5) Monitoring
---
This term project is a part of Data Streaming and Real Time Analytics subject of a Master's Degree in Business Analytics and Data Science (BADS) at National Institute of Development Administration (NIDA).   

It's about IoT project that getting PM2.5 from dust sensors and collecting them in AWS DynamoDB.
There are 3 parts of this project   
1) Web application (querying data from AWS DynamoDB and showing them as dashboard)   
2) Scheduler (sending updated PM2.5 messages every 1 hour to Line application using AWS lambda function and setting scheduler by AWS CloudWatch)   
3) Line Chatbot (handling messages of rich menu from Line application)   

## IoT Component
- ESP32
- PMSA003 dust sensor

## AWS Products involved
- EC2
- DynamoDB
- Lambda function
- CloudWatch

## Team member
1) Phupathsorn Harnprab   
2) Benya Jitjongruck   
3) Rawit Samaisenee   
4) Thanawat Polcharoen   
5) Narongsak Kowwilaisang  