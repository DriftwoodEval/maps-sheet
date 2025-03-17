# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas",
# ]
# ///
import pandas as pd
import argparse

def open_sheet(file):
    with open(file, "r", errors="ignore") as f:
        df = pd.read_csv(f)
        return df

def filter_by_status(df):
    return df[df.STATUS != "Inactive"]

def normalize_names(df):
    for col in ["LASTNAME", "FIRSTNAME", "PREFERRED_NAME"]:
        df[col] = (
            df[col].str.title().replace({"Iii": "III", "Ii": "II"}, regex=True)
        )
    return df

def add_whole_name(df):
    df["FULLNAME"] = df.apply(
        lambda row: row.PREFERRED_NAME + " " + row.LASTNAME
        if pd.notna(row.PREFERRED_NAME)
        else row.FIRSTNAME + " " + row.LASTNAME,
        axis=1,
    )
    return df

def add_full_address(df):
    df["USER_ADDRESS_ZIP"] = df["USER_ADDRESS_ZIP"].str.replace(r"- ?$", "", regex=True)
    df["FULLADDRESS"] = df.apply(
        lambda row: " ".join(
            (field for field in [
                row.USER_ADDRESS_ADDRESS1,
                row.USER_ADDRESS_ADDRESS2,
                row.USER_ADDRESS_ADDRESS3,
                ",",
                f"{row.USER_ADDRESS_CITY},",
                row.USER_ADDRESS_STATE,
                row.USER_ADDRESS_ZIP
            ] if isinstance(field, str) and field.strip() and field.lower() != 'nan')
        ).replace(" ,", ","),
        axis=1,
    )
    return df

def prune_columns(df):
    df = df[["FULLNAME", "FULLADDRESS"]]
    return df

def remove_test_names(df, test_names):
    return df[~df.FULLNAME.isin(test_names)]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, default="demographic.csv")
    args = parser.parse_args()

    df = open_sheet(args.file)
    df = filter_by_status(df)
    df = normalize_names(df)
    df = add_whole_name(df)
    df = add_full_address(df)
    df = prune_columns(df)
    df = remove_test_names(df, ["Testman Testson", "Testman Testson Jr.", "Johnny Smonny", "Johnny Smonathan", "Test Mctest"])
    df.to_csv("maps.csv", index=False)


if __name__ == "__main__":
    main()
