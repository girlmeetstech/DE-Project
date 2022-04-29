import argparse
import os
import sys
from datetime import date
from pyspark import SparkConf
from pyspark.sql import SparkSession, SQLContext


def main():
    input_path = "oci://DE-Bucket@orasenatdpltintegration03/NYT-" + today
    pre, ext = os.path.splitext(input_path)
    today = datetime.date.today()
    output_path = "oci://DE-Output-Bucket@orasenatdpltintegration03/NYT-" + today
    print(output_path)

# Set up Spark.
    spark_session = get_dataflow_spark_session()
    sql_context = SQLContext(spark_session)

# Load our data.
    input_dataframe = spark_session.read.json(path=input_path, multiLine="true")
    input_dataframe.show()

# Save the results as CSV.
input_dataframe.write.csv(path=output_path, header="true", mode="overwrite")

# Show on the console that something happened.
    print("Successfully converted {} rows to csv and wrote to {}.".format(input_dataframe.count(), output_path))
def get_dataflow_spark_session(
    app_name="DataFlow", file_location=None, profile_name=None, spark_config={}
):
    """
    Get a Spark session in a way that supports running locally or in Data Flow.
    """
    if in_dataflow():
        spark_builder = SparkSession.builder.appName(app_name)
    else:
        # Import OCI.
        try:
            import oci
        except:
            raise Exception(
                "You need to install the OCI python library to test locally"
            )
# Use defaults for anything unset.
        if file_location is None:
            file_location = oci.config.DEFAULT_LOCATION
        if profile_name is None:
            profile_name = oci.config.DEFAULT_PROFILE
# Load the config file.
        try:
            oci_config = oci.config.from_file(
                file_location=file_location, profile_name=profile_name
            )
        except Exception as e:
            print("You need to set up your OCI config properly to run locally")
            raise e
        conf = SparkConf()
        conf.set("fs.oci.client.auth.tenantId", oci_config["tenancy"])
        conf.set("fs.oci.client.auth.userId", oci_config["user"])
        conf.set("fs.oci.client.auth.fingerprint", oci_config["fingerprint"])
        conf.set("fs.oci.client.auth.pemfilepath", oci_config["key_file"])
        conf.set(
            "fs.oci.client.hostname",
            "https://objectstorage.{0}.oraclecloud.com".format(oci_config["region"]),
        )
        spark_builder = SparkSession.builder.appName(app_name).config(conf=conf)
# Add in extra configuration.
    for key, val in spark_config.items():
        spark_builder.config(key, val)
# Create the Spark session.
    session = spark_builder.getOrCreate()
    return session
def in_dataflow():
    """
    Determine if we are running in OCI Data Flow by checking the environment.
    """
    if os.environ.get("HOME") == "/home/dataflow":
        return True
    return False
if __name__ == "__main__":
    main()
