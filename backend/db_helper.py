import mysql.connector
from contextlib import contextmanager

@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="butta@akhil70",
        database="expense_manager"
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    print("Closing cursor")
    cursor.close()
    connection.close()


def fetch_all_records():
    query = "SELECT count(*) from expenses"

    with get_db_cursor() as cursor:
        cursor.execute(query)
        expenses = cursor.fetchall()
        return expenses



def fetch_expenses_for_date(expense_date):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def insert_expense(expense_date, amount, category, notes):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def delete_expenses_for_date(expense_date):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def fetch_expenses_summary(start_date,end_date):
    with get_db_cursor() as cursor:
        cursor.execute(
            '''
                select category,sum(amount) as total from expenses 
                where expense_date between %s and %s
                group by category
            ''',
            (start_date,end_date)
        )
        expenses = cursor.fetchall()
        return expenses

def fetch_expenses_monthly():
    with get_db_cursor() as curosr:
        curosr.execute(
            '''
                SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month, SUM(amount) AS total_amount
                FROM expenses
                GROUP BY month
                ORDER BY month;
            '''
        )
        expenses=curosr.fetchall()
        return expenses
    
if __name__ == "__main__":
    # summary=fetch_expenses_summary("2024-08-01","2024-08-05")
    # for data in summary:
    #     print(data)
    print(fetch_expenses_monthly())