from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.schema import ChatMessage
from langchain.llms import OpenAI
from datetime import timedelta
from datetime import datetime
import streamlit as st
from PIL import Image
import datetime as dt
import requests
import asyncio
import base64
import time

from yahooquery import Ticker
import yfinance as yf

st.set_page_config(page_title = "Dater", page_icon = "🌌️", layout = "wide", initial_sidebar_state = "expanded")
container = st.container()
img = Image.open("./Backgrounds/White Template Logo.png")
img = img.resize((300, 75))
container.image(img)

openai_api_key = "OPEN_API_KEY"
gnews_api_key = "GNEWS_API_KEY"

class Background:
	def __init__(self, img):
		self.img = img
	def set_back_side(self):
		side_bg_ext = 'png'
		side_bg = self.img

		st.markdown(
		f"""
		<style>
			[data-testid="stSidebar"] > div:first-child {{
				background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
			}}
		</style>
		""",
		unsafe_allow_html = True,
		)

class StreamHandler(BaseCallbackHandler):
	def __init__(self, container, initial_text = ""):
		self.container = container
		self.text = initial_text

	def on_llm_new_token(self, token: str, **kwargs) -> None:
		self.text += token
		self.container.markdown(self.text)

class Fundamental:
	def __init__(self):
		self.back = Background('./Backgrounds/augmented_bulb_2.png')
		self.back.set_back_side()
		self.query = "Please, give me an exahustive fundamental analysis about the companies that you find in the documented knowledge. I want to know the pros and cons of a large-term investment. Please, base your answer on what you know about the company, but also on wht you find useful about the documented knowledge. I want you to also give me your opinion in, if it is worthy to invest on that company given the fundamental analysis you make. If you conclude that is actually wise to invest on a given company, or in multiple companies (focus only on the ones in the documented knowledge and use the financial statement data provided to enhance your fundamental analysis even further) then come up also with some strategies that I could follow to make the best out of my investments. Make sure to show all the operations you make, given the data in the financial statements. Show the results of the Revenue Growth, ROE, Dividends, Price to Earnings, Market Tredns and Industry Performance, company's leadership practices, economic indicators, competitive position, regulatory environments, book value, etc. I want to see all the indicators you can get from this information."
		self.llm = OpenAI(model_name = "gpt-4-1106-preview", temperature = 0, streaming = True, api_key = openai_api_key)
		self.tools = load_tools(["ddg-search"])
		self.agent = initialize_agent(self.tools, self.llm, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = False)
		self.prompt_template = " stock symbol(s). Return only the symbols separated by spaces. Don't add any type of punctuation. If you already know the answer, there is no need to search for it on duckduck go"
		self.DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The
		AI is an AI-powered fundamental analyst. It uses Documented Information to give fundamental insights on an asset determined by the user. It is specific, and gives full relevant
		perspective to let the user know, if it is worthy to make investment on a certain asset, and can also build intelligent strategies with the given information, as well as from intel that it
		already knows, or will generate. Take into account, that the documented knowledge comes in the next structure. **Title:** (Message of the Title), **Description:** (Message of the
		Description)\n\n, and so on. All articles from the documented knowledge have a title and a description (both of which are separated by comas), and all articles are separated with the \n\n
		command between one another. The AI will also use the Financial Statements of they are provided. NOTE: As you know, Financial statements are VERY important for the fundamental analysis, so 			use them wizely in order to give the best financial statement there could be in the world. Show the operations you make for the fundamental analysis as you make it.
		Each financial statement will be separated in function of the company/asset the belong to. So be sure to make that fundmental analysis using the financial statement belonging to the one
		company you are analyzing.

		Documented Information:
		{docu_knowledge},

		Financial Statements:
		{financial_statement}

		(You do not need to use these pieces of information if not relevant)

		Current conversation:
		Human: {input}
		AI-bot:"""

	async def get_stock_symbol(self, company_name):
		st_callback = StreamlitCallbackHandler(st.container())
		search_results = self.agent.run(company_name + self.prompt_template, callbacks = [st_callback])
		symbols = search_results.split(" ")
		return symbols

	async def get_fin_statements(self, symbol):
		df = Ticker(symbol)
		df1 = df.income_statement().reset_index(drop = True).transpose()
		df2 = df.balance_sheet().reset_index(drop = True).transpose()
		df3 = df.cash_flow().reset_index(drop = True).transpose()
		return df1, df2, df3

	async def get_stock_history(self, symbol, date):
		ticker = yf.Ticker(symbol)
		data = ticker.history(start = "2019-01-01", end = date)
		return data

	async def get_latest_price(self, data):
		latest_price = data['Close'].iloc[-1]
		return latest_price

	def get_gnews_api(self):
		url = "https://gnews.io/api/v4/top-headlines?lang=en&token=<gnews_api_key>"
		response = requests.get(url)
		news = response.json()
		return news

	def get_gnews_api_spec(self, search_term):
		url = f"https://gnews.io/api/v4/search?q={search_term}&token=<gnews_api_key>"
		response = requests.get(url)
		news = response.json()
		return news

	def get_response(self, user_message, docu_knowledge, financial_statement, temperature = 0):

		PROMPT = PromptTemplate(input_variables = ['input','docu_knowledge','financial_statement'], template = self.DEFAULT_TEMPLATE)

		stream_handler = StreamHandler(st.empty())
		chat_gpt = ChatOpenAI(streaming = True, callbacks = [stream_handler], temperature = temperature, model_name = "gpt-4-1106-preview")
		conversation_with_summary = LLMChain(llm = chat_gpt, prompt = PROMPT, verbose = True)
		output = conversation_with_summary.predict(input = user_message, docu_knowledge = docu_knowledge, financial_statement = financial_statement)

		return output

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

		if "messages" not in st.session_state:
			st.session_state["messages"] = [ChatMessage(role = "assistant", content = "")]

		with st.form(key = 'company_search_form'):
			company_name = st.text_input("Enter a company name:")
			submit_button = st.form_submit_button("Search", type = "primary")

		if submit_button and company_name:
			articles_string = ""
			financial_statement = ""
			symbols = await self.get_stock_symbol(company_name)
			cont_api = 0

			for symbol in symbols:
				
				with st.spinner("Searching..."):
					gnews_api_spec = self.get_gnews_api_spec(symbol)
					try:
						income_statement, balance_sheet, cash_flow = await self.get_fin_statements(symbol)

						financial_statement += (f"{symbol}") + "\n\n"
						df_price = await self.get_stock_history(symbol, date_d)
						stock_price = await self.get_latest_price(df_price)
						financial_statement += "Current Market Price:" + "\n\n"
						financial_statement += (f"{stock_price}") + "\n\n"
						financial_statement += "Income Statement:" + "\n\n"
						financial_statement += income_statement.to_string() + "\n\n"
						financial_statement += "Balance Sheet:" + "\n\n"
						financial_statement += balance_sheet.to_string() + "\n\n"
						financial_statement += "Cash Flow:" + "\n\n"
						financial_statement += cash_flow.to_string() + "\n\n"

					except:
						st.subheader(f":red[Financial Statement for _{symbol}_ couldn't be found 😥️]")
					with st.sidebar:
						with st.expander(symbol):
							st.subheader("News from GNews API", divider = 'rainbow')
							for article in gnews_api_spec['articles']:
								st.write(f"**Title:** {article['title']}")
								st.write(f"**Description:** {article['description']}")
								st.write(f"**URL:** {article['url']}")
								st.markdown("""---""")
								article_string = f"**Title:** {article['title']}, **Description:** {article['description']} \n"
								articles_string += article_string + "\n"
				time.sleep(1)
			try:
				with st.sidebar:
					with st.spinner("Searching..."):
						gnews_api = self.get_gnews_api()
						with st.expander("General News"):
							st.subheader("News from GNews API", divider = 'rainbow')
							for article in gnews_api['articles']:
								st.write(f"**Title:** {article['title']}")
								st.write(f"**Description:** {article['description']}")
								st.write(f"**URL:** {article['url']}")
								st.write("---")
								article_string = f"**Title:** {article['title']}, **Description:** {article['description']} \n"
								articles_string += article_string + "\n"
			except:
				pass

			#st.write(financial_statement)

			with st.chat_message("assistant"):
				user_input = self.query
				output = self.get_response(user_input, articles_string, financial_statement, temperature = 0)
				st.session_state.messages.append(ChatMessage(role = "assistant", content = output))

if __name__ == "__main__":
	fundamental = Fundamental()
	asyncio.run(fundamental.run())
