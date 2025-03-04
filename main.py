import gradio as gr
import os
import books_db_actions as db
from init_config import config
import pandas as pd


def get_books(user_input):
    if user_input:
        print(f"Searching books for author: {user_input}")

        query = f"""select b."name", b.number_of_sales, b.reviews from authors a
                    join book b on a.author_id = b.author_id
                    where a."name" = '{user_input}'
                    order by b.number_of_sales desc;"""

        response = db.get_data(query, database_config)

        print(f"Response from database: {response}")

        df = pd.DataFrame(response)
        if df.empty:
            return "No books found for this author "
        else:
            return df
    else:
        raise Exception("You need to insert an author before pressing the button")


def add_book(name, sales, review, author):
    if not name or not sales or not review or not author:
        return "All fields are mandatory", ""

    if not sales.isdigit():
        return "Sales parameter must be a positive number", ""

    sales = int(sales)
    if sales <= 0:
        return "Sales must be a positive number", ""

    try:
        review = float(review)
        if review < 0 or review > 10:
            return "Review must be between 0 and 10", ""
    except ValueError:
        return "Review parameter must be a number between 0 and 10", ""

    author_data = db.get_data("""SELECT author_id FROM authors WHERE "name" = %s LIMIT 1;""", database_config,
                              (author,))

    if author_data:
        author_id = author_data[0]['author_id']
        query = """INSERT INTO book ("name", number_of_sales, reviews, author_id) 
                   VALUES (%s, %s, %s, %s)"""
        db.insert_row(query, (name, sales, review, author_id), database_config)
        print(f"Book '{name}' added successfully ")
        return f"Book '{name}' added successfully ", ""
    else:
        return f"Author '{author}' not found ", ""


def delete_book(name):
    if name:
        db.delete_row(name, database_config)
        return f"Book '{name}' deleted successfully"
    else:
        return "Book name is mandatory for delete"


def table_change(table, author_name):
    print(f"Comparing table for author: {author_name}")
    original_table = get_books(author_name)

    if isinstance(original_table, pd.DataFrame) and isinstance(table, pd.DataFrame):
        diff = original_table.compare(table)
        if not diff.empty:
            print("Changes detected: ", diff)
            return diff
        else:
            print("No changes detected")
            return original_table
    else:
        print("Invalid data for comparison")
        return table



def start_gui_app():
    with gr.Blocks() as app:
        gr.HTML("""
        <style>
            .gradio-container {
                background-color: #f0f0f0;
                border-radius: 15px;
                padding: 20px;
            }
            #author_input {
                background-color: #e0e0e0;
                font-size: 16px;
                padding: 10px;
            }
            #get_books_button {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            #get_books_button:hover {
                background-color: #45a049;
            }
            #results_table {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-top: 20px;
            }
        </style>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                text_input = gr.Textbox(label="Write an author", elem_id="author_input")
            with gr.Column(scale=1):
                get_books_button = gr.Button("Show Books", elem_id="get_books_button")

        with gr.Row():
            response_table = gr.Dataframe(label="Results", elem_id="results_table")
            response_table.change(fn=table_change, inputs=[response_table, text_input], outputs=response_table)
            get_books_button.click(fn=get_books, inputs=text_input, outputs=response_table)

        with gr.Row():
            with gr.Column(scale=1):
                new_book = gr.Textbox(label="New Book", elem_id="new_book_input")
            with gr.Column(scale=1):
                number_of_sales = gr.Textbox(label="Sales", elem_id="sales_input")
            with gr.Column(scale=1):
                review = gr.Textbox(label="Review", elem_id="review_input")
            with gr.Column(scale=1):
                author = gr.Textbox(label="Author Name", elem_id="author_name_input")

        with gr.Row():
            add_book_button = gr.Button("Add Book", elem_id="add_book_button")
            output_message = gr.Textbox(label="Output Message", interactive=False)
            add_book_button.click(fn=add_book, inputs=[new_book, number_of_sales, review, author],
                                  outputs=output_message)

        with gr.Row():
            with gr.Column(scale=1):
                delete_book_input = gr.Textbox(label="Delete Book Name", elem_id="delete_book_input")
            with gr.Column(scale=1):
                delete_book_button = gr.Button("Delete Book", elem_id="delete_book_button")
            delete_book_button.click(fn=delete_book, inputs=delete_book_input, outputs=output_message)

    app.launch(inbrowser=True, show_error=True)


if __name__ == '__main__':
    database_config = config.get("database_config")
    database_config['password'] = os.environ['dbeaver_pass']
    start_gui_app()
