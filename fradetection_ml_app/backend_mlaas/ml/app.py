# load data into postgres
# train model if not present


# load new data into post gress under different tables
# produce the new predictions and push it to a column in the new table


from LoadAndTrain import LoadDataAndTrain



if __name__ == "__main__":
    pipeline = LoadDataAndTrain(
        db_name="mlapp",
        user="postgres",
        password="pass",
        host="localhost",
        port="5432",
        csv_path="data/creditcard.csv",
        table_name="transactions"
    )

    pipeline.run_pipeline()
