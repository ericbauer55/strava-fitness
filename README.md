# Strava Fitness
Strava is a fitness mobile app that allows users to track various exercise activities as well as interact with a community of athletes. It has been a substantial part of my fitness journey since 2020 and remains my default method of tracking progress. By 2022, I had built up a dataset of 226 rides over ~2700 miles and I wanted to leverage it to answer the overall question:

```How can I model my fitness to improve its consistency and growth?```

There are many ways to [track my fitness](https://www.youtube.com/watch?v=x-ty9x6-P1o):
1.  Rating of Perceived Exertion ([RPE](https://ludum.com/blog/data-performance-analytics/rpe-as-a-training-load-score/)) as a subjective 10-point scale 
2.  Benchmark Hill Climb – time trial (optionally w/ heart rate) every 8 weeks
3.  Functional Threshold Power (FTP) Test – max constant power in 1 hour
4.  Improving Power Numbers – Peak Power Curves
5.  Training Impulse ([TRIMP](https://ludum.com/blog/data-performance-analytics/trimp-as-a-training-load-score/)) to track exertion durations within cardio zones

Since I was only just starting my biking in 2020, my data collection relied only on Strava's app to capture data. This means that methods like 3, 4 or 5 weren't feasible as I did not own power meters for my bike or a heartrate monitor for me. I had not been periodically testing my hill climb times, so method 1 was the most practical with the existing data set.

## Exploratory Data Analysis
Strava allows all activity data to be exported as .GPX files. These are XML-styled logs of timestamps and GPS coordinates in their most basic form. They can be compiled into a time series data set with the correct extraction, transformation and loading (ETL). The details of how to explore such a GPX dataset are detailed in the pre-cursor repo [Strava EDA](https://github.com/ericbauer55/strava-eda)!

## Modeling Problem Statement
In order to understand my Rating of Perceived Effort for each ride, I wanted to understand what features (average speed, peak power, etc.) contribute most towards which RPE. Thus I built a multinomial classifier model out of a Random Forest and a Logistic Regression in order to classify each ride as `{EASY, MEDIUM, HARD}`. This set of classes compresses the 10 different RPE categories typically available. This compression was done in order to handle the relatively small set of suitable rides that I had collected data for. I also chose the classical ML models that I did in order to easily interpret feature importances later when extracting fitness insights.

## Data Science Project Flow (Presentation)
Since this project was accelerated and finished rather quickly, the details of the process aren't as documented via README or wiki as I would like. However, the presentation encapsulating the entire data science flow for this problem [is available here.](https://docs.google.com/presentation/d/13JOcauPiCkfQYyBHhYVbpmKj09zW45ka/edit?usp=sharing&ouid=115196734684094815079&rtpof=true&sd=true) Feel free to message me with any questions

## Closing Thoughts
Although the chosen models did not perform well on the test set, this project demonstrates a complete data science thought process on a homegrown dataset and personal data quest. Ultimately, targeting a subjective measure like RPE with only 186 valid ride time series is a difficult task. There are 4 avenues for improvement for this process:

1. :bicyclist:**Collecting More Data**: Riding the bike more is never a bad thing, and if collecting data is a side-motivation for maintaining fitness--then so be it!
2. :heartbeat:**Collecting/Distilling Better Features**: Purchasing a fitness device that can log heart rate on the GPX files will be crucial for directly measuring a key cardio state! A bike power meter can help too.
3. :traffic_light:**Utilize Suitable Deep Learning Models**: Models like RNNs or LSTMs could have a distinct advantage in gauging the RPE of a ride. Such models are useful for sentiment analysis for text, but the RPE scored after a ride is completed is also a sentiment by the user. Using these models can help weight the more recent information as well as accumulated effort from ride data. After all, I may have been more likely to rate the ride based on the last thing I did before ending the ride (ex: an arduous uphill climb vs. an easy downhill coast).
4. :chart_with_upwards_trend:**Analyze More Users**: In order to utilize deep learning methods--or indeed, have more success with classical models--considering data from many more users will unlock more generalizable insights.
