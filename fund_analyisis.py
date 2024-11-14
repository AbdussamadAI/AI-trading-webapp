import streamlit as st
from langchain.llms import OpenAI
import asyncio
from datetime import datetime

st.set_page_config(page_title = "Fundamental Analysis", page_icon = "🎆️", layout = "wide", initial_sidebar_state = "expanded")

openai_api_key = "OPEN_API_KEY"

class Fundamental:
	def __init__(self):
		self.llm = OpenAI(model_name = "gpt-4-1106-preview", temperature = 0, streaming = True, api_key = openai_api_key)

	async def run(self):
		date_now = datetime.now()
		date_year = date_now.year
		date_month = date_now.month
		date_day = date_now.day
		date_day_ = date_now.strftime("%A")

		date_d = "{}-{}-{}".format(date_year, date_month, date_day)

		st.title(":orange[Welcome!]")
		st.subheader(f" _{date_d}_")
		st.subheader(f" :orange[_{date_day_}_]", divider = 'rainbow')

if __name__ == "__main__":
	fundamental = Fundamental()
	asyncio.run(fundamental.run())
