from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.llms import OpenAI
from datetime import datetime
import streamlit as st
from PIL import Image
import asyncio
import base64
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title = "Dater", page_icon = "🌌️", layout = "wide", initial_sidebar_state = "expanded")
container = st.container()
img = Image.open("./Backgrounds/White Template Logo.png")
img = img.resize((300, 75))
container.image(img)

openai_api_key = "API_KEY"

class Technical:
	def __init__(self):
		self.llm = OpenAI(model_name = "gpt-4-1106-preview", temperature = 0, streaming = True, api_key = openai_api_key)
		self.tools = load_tools(["ddg-search"])
		self.agent = initialize_agent(self.tools, self.llm, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = False)
		self.prompt_template = " stock symbol(s). Return only the symbols separated by spaces. Don't add any type of punctuantion. If you already know the answer, there is no need to search for it on duckduck go"

	async def get_stock_symbol(self, company_name):
		st_callback = StreamlitCallbackHandler(st.container())
		search_results = self.agent.run(company_name + self.prompt_template, callbacks = [st_callback])
		symbols = search_results.split(" ")
		return symbols

	async def get_stock_history(self, symbol, date):
		ticker = yf.Ticker(symbol)
		data = ticker.history(start = "2015-01-01", end = date)
		return data

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

		with st.form(key = 'company_search_form'):
			company_name = st.text_input("Enter a company name:")
			submit_button = st.form_submit_button("Search", type = "primary")

		if company_name:
			symbols = await self.get_stock_symbol(company_name)

			for symbol in symbols:

				left_column, _ = st.columns(2)
				with left_column:
					st.header(symbol)
				plot_placeholder = st.empty()
				st.markdown("""---""")

				df = await self.get_stock_history(symbol, date_d)
				df.ta.rsi(length = 14, append = True)
				df.ta.macd(fast = 12, slow = 26, signal = 9, append = True)
				df.ta.bbands(length = 20, append = True)

				data_date = df.index.to_numpy()
				data_open_price = df['Open'].to_numpy()
				data_high_price = df['High'].to_numpy()
				data_low_price = df['Low'].to_numpy()
				data_close_price = df['Close'].to_numpy()

				#indicators
				rsi = df['RSI_14'].to_numpy()
				macd = df['MACD_12_26_9'].to_numpy()
				macdh = df['MACDh_12_26_9'].to_numpy()
				macds = df['MACDs_12_26_9'].to_numpy()
				bbl = df['BBL_20_2.0'].to_numpy()
				bbm = df['BBM_20_2.0'].to_numpy()
				bbu = df['BBU_20_2.0'].to_numpy() 

if __name__ == "__main__":
	technical = Technical()
	asyncio.run(technical.run())
