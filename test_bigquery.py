from google.cloud import bigquery
import matplotlib.pyplot as plt

# Authenticate
client = bigquery.Client.from_service_account_json("credentials.json")

# Example query
query = """
SELECT country, city, AVG(value) AS avg_pm25
FROM `bigquery-public-data.openaq.global_air_quality`
WHERE pollutant = 'pm25'
GROUP BY country, city
ORDER BY avg_pm25 DESC
LIMIT 10;
"""

df = client.query(query).to_dataframe()
print(df)

# Save results to CSV and Excel
df.to_csv("air_quality_results.csv", index=False)

# Needs openpyxl for Excel
df.to_excel("air_quality_results.xlsx", index=False)

print("Results saved as air_quality_results.csv and air_quality_results.xlsx")

# Visualize results (Bar Chart)
df.plot(kind="bar", x="city", y="avg_pm25", figsize=(10,5), legend=False)
plt.ylabel("Average PM2.5")
plt.title("Top Polluted Cities (PM2.5)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
