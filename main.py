import streamlit as st
import altair as alt
import pandas as pd


class crypto_dashboard:
    def __init__(self):
        lowercase = lambda x: str(x).lower()
        self.cp_data = pd.read_csv('data/20210715_cp.csv')
        self.cp_data['token'] = 'crypto_punks'
        self.cp_data.rename(lowercase, axis='columns', inplace=True)
        self.cp_data.columns = self.cp_data.columns.str.replace(' ', '')


        self.ab_data = pd.read_csv('data/20210715_artblocks.csv')
        self.ab_data['token'] = 'art_blocks'
        self.ab_data.rename(lowercase, axis='columns', inplace=True)
        self.ab_data.columns = self.cp_data.columns.str.replace(' ', '')


        self.cv_data = pd.read_csv('data/20210715_cv.csv')
        self.cv_data['token'] = 'crypto_voxels'
        self.cv_data.rename(lowercase, axis='columns', inplace=True)
        self.cv_data.columns = self.cp_data.columns.str.replace(' ', '')

        self.hm_data = pd.read_csv('data/20210715_hm.csv')
        self.hm_data['token'] = 'hash_masks'
        self.hm_data.rename(lowercase, axis='columns', inplace=True)
        self.hm_data.columns = self.cp_data.columns.str.replace(' ', '')
        
        self.bayc_data = pd.read_csv('data/20210715_bayc.csv')
        self.bayc_data['token'] = 'bored_apes'
        self.bayc_data.rename(lowercase, axis='columns', inplace=True)
        self.bayc_data.columns = self.cp_data.columns.str.replace(' ', '')
        
        self.dland_data = pd.read_csv('data/20210715_dland.csv')
        self.dland_data['token'] = 'decentraland'
        self.dland_data.rename(lowercase, axis='columns', inplace=True)
        self.dland_data.columns = self.cp_data.columns.str.replace(' ', '')
        
        self.mcats_data = pd.read_csv('data/20210715_mcats.csv')
        self.mcats_data['token'] = 'mooncats'
        self.mcats_data.rename(lowercase, axis='columns', inplace=True)
        self.mcats_data.columns = self.cp_data.columns.str.replace(' ', '')

        self.meebits_data = pd.read_csv('data/20210715_meebits.csv')
        self.meebits_data['token'] = 'meebits'
        self.meebits_data.rename(lowercase, axis='columns', inplace=True)
        self.meebits_data.columns = self.cp_data.columns.str.replace(' ', '')

        frames = [self.cp_data, self.ab_data, self.bayc_data, self.dland_data, self.mcats_data, self.cv_data, self.hm_data, self.meebits_data]
        self.all_data = pd.concat(frames)
        self.all_data = self.all_data[self.all_data['from_address'] != ' 0x0000000000000000000000000000000000000000']

        self.selected_data = self.all_data[['eth_value', 'blk_timestamp','token','from_address','to_address']].groupby(['blk_timestamp','token','from_address','to_address'], as_index=False).sum()
        min = self.selected_data['blk_timestamp'].min()
        self.selected_data = self.selected_data[self.selected_data['eth_value'] > 1]
        self.selected_data['blk_timestamp'] = self.selected_data['blk_timestamp'] - min
        self.selection = alt.selection_multi(fields=['token'])

        self.top_10_b = None
        self.top_10_s = None
        self.top_100_s_time = None
        self.buyer_overlap = None
        self.seller_overlap = None

    def transactions_over_time(self):
        self.selection = alt.selection_multi(fields=['token'])
        self.selection_2 = alt.selection_multi(fields=['from_address'])
        self.bubble = alt.Chart(title="Total ETH Per Token (Interactive Select Bubble To Filter. Hold Shift to Select Multiple").mark_circle()\
            .encode(
            x='token:N',
            size=alt.Size('sum(eth_value):Q', scale=alt.Scale(range=[5000, 20000]), legend=None),
            color=alt.condition(self.selection, alt.value('steelblue'), alt.value('lightgray')))\
            .properties(width=1200, height=600)\
            .add_selection(self.selection)

        self.top_100_s_time = alt.Chart(title="Time Series of Median NFT transactions Size in ETH") \
            .mark_area()\
            .encode(
                alt.X('blk_timestamp:O', axis=None),
                alt.Y('median(eth_value):Q', scale=alt.Scale(domain=(0, 10),clamp=True)),
                color='token:N') \
            .properties(width=1200, height=600)\
            .transform_filter(self.selection)

        self.top_100_s_time.save('charts/top_100_sellers_by_eth_over_time.html')
        self.concat_graph_1 = alt.vconcat(self.bubble, self.top_100_s_time, data=self.selected_data)

        #data = self.all_data[['from_address', 'token', 'eth_value']].groupby(['from_address', 'token'],as_index=False).sum()
        #data = data.sort_values(ascending=False, by='eth_value').head(50)

        self.seller_overlap = alt.Chart(title="Top 50 Sellers") \
            .mark_bar() \
            .transform_aggregate(
            sum_eth='sum(eth_value):Q',
            groupby=["from_address","token"])\
            .transform_window(
            rank="rank(sum_eth)",
            sort=[alt.SortField('sum_eth', order='descending')]) \
            .transform_filter(self.selection) \
            .transform_filter(alt.datum.rank < 50)\
            .encode(x='sum_eth:Q',
                    y=alt.Y('from_address:N',sort='-x'),
                    color='token:N')\
            .properties(width=500, height=1000)
        #data = self.all_data[['to_address', 'token', 'eth_value']].groupby(['to_address', 'token'],as_index=False).sum()
        #data = data.sort_values(ascending=False, by='eth_value').head(50)

        self.buyer_overlap = alt.Chart(title="Top 50 Buyers") \
            .mark_bar() \
            .transform_aggregate(
            sum_eth='sum(eth_value):Q',
            groupby=["to_address","token"])\
            .transform_window(
            rank="rank(sum_eth)",
            sort=[alt.SortField('sum_eth', order='descending')]) \
            .transform_filter(self.selection) \
            .transform_filter(alt.datum.rank < 50)\
            .encode(x='sum_eth:Q',
                    y=alt.Y('to_address:N',sort='-x'),
                    color='token:N')\
            .properties(width=500, height=1000)
        self.buyer_overlap.save('charts/buyer_overlap.html')

        self.b2s = alt.Chart(title="Web of Buyers to Sellers").transform_window(
            count_of_transactions='count()'
        ).transform_fold(
            ['from_address', 'to_address']
        ).mark_line().encode(
            x='key:N',
            y = alt.Y('count_of_transactions:Q', axis=None),
            color='token:N',
            detail='value:N',
            opacity=alt.value(0.1)
        ).properties(width=1200, height=2000)\
        .transform_filter(
            self.selection
        )
        self.b2s.save('charts/bs.html')
        self.concat_graph_2 = alt.hconcat(self.seller_overlap,self.buyer_overlap, data=self.selected_data)
        self.seller_overlap.save('charts/seller_overlap.html')
        self.concat_graph_3 = alt.vconcat(self.concat_graph_1 ,self.concat_graph_2,self.b2s, data=self.selected_data)

    def buy_overlap(self):
        data = self.all_data[['to_address', 'token', 'eth_value']].groupby(['to_address', 'token'],as_index=False).sum()
        data = data.sort_values(ascending=False, by='eth_value').head(50)
        self.buyer_overlap = alt.Chart(data) \
            .mark_bar() \
            .encode(x='sum(eth_value):Q',
                    y=alt.Y('to_address:N', sort='-x'),
                    color='token:N').properties(width=1000, height=1000)

        self.buyer_overlap.save('charts/buyer_overlap.html')

    def top_10_sellers(self):
        df_eth_sum = self.cp_data[['from_address','eth_value']]
        df_eth_sum = df_eth_sum.sort_values(ascending=False, by='eth_value').head(50)
        self.top_10_s = alt.Chart(df_eth_sum).mark_bar().encode(x='from_address:O', y ='eth_value:Q').properties(width=1000, height=1000)

        self.top_10_s.save('charts/top_10_sellers_by_eth.html')

    def top_10_buyers(self):
        df_eth_sum = self.cp_data[['to_address', 'eth_value']]
        df_eth_sum = df_eth_sum.sort_values(ascending=False, by='eth_value').head(50)
        self.top_10_b = alt.Chart(df_eth_sum).mark_bar().encode(x='to_address:O', y ='eth_value:Q').properties(width=1000, height=1000)

        self.top_10_b.save('charts/top_10_buyers_by_eth.html')

    def buyers_to_sellers_2(self):
        input_dropdown = alt.binding_select(options=['crypto_punks', 'art_blocks', 'crypto_voxels', 'hash_masks', 'bored_apes', 'decentraland', 'mooncats', 'meebits'], name='Tokens')
        selection = alt.selection_single(fields=['token'], bind=input_dropdown)

        data = self.all_data[['from_address', 'to_address', 'token', 'eth_value']].groupby(['from_address', 'to_address', 'token'],as_index=False).sum()
        data = data.sort_values(ascending=False, by='eth_value').head(1000)
        self.b2s = alt.Chart(data).transform_window(
            sort=[{'field': 'from_address'}],
            index='count()'
        ).transform_fold(
            ['from_address','to_address']
        ).mark_line().encode(
            x='key:N',
            y='value:Q',
            color='token:N',
            detail='eth_value:Q',
            opacity=alt.value(0.5)
        ).properties(width=1000, height=1000)\
        .add_selection(
            selection
        ).transform_filter(
            selection
        )

    def streamlit_app(self):
        st.set_page_config(layout="wide")
        st.title('Analysis of Popular NFTs')
        #st.altair_chart(self.bubble, use_container_width=True)
        st.altair_chart(self.concat_graph_3, use_container_width=True)
        with st.sidebar:
            st.title("Project Description")
            with st.container():
                st.title("Data")
                st.markdown('The data for this project came from a paper called, "Networks of Ethereum Non-Fungible Tokens: A graph-based analysis of the ERC-721 ecosystem" ')
                st.markdown('Link -> https://arxiv.org/abs/2110.12545')
                st.markdown("Data -> https://github.com/epfl-scistimm/2021-ieee-blockchain")
                st.title("Goals")
                st.markdown("The Goal of this project was to perform basic data analysis to establish when and who were buying these popular Tokens.")
                st.title("Tasks")
                st.markdown("The user is using the visualization to gain knowledge of NFT transactions")
                st.markdown("The user will interact with the graphs to see when NFTs are being sold, who is buying the NFTs, and how many are they buying.")
                st.markdown("The user is looking for addresses that buy and sell. They are looking for peaks and they are looking for trends.")
            st.title("Component description top to bottom")
            with st.container():
                st.title("Bubble Chart")
                st.markdown("The first component is interactive and filters the charts below it for a specific token project. "
                            "The size of the bubble is indicative of the total ETH sold. The purpose is to allow the user to "
                            "filter the data and to provide an indication of the amount of ETH transacted.")
            with st.container():
                st.title("Time Series")
                st.markdown("The second component shows a time series of transactions between the first and last block of "
                            "the blockchain data. The purpose is to give the user a view of when each project was popular "
                            "and the scale of the transactions taking place")
            with st.container():
                st.title("Top NFT Buyers and Sellers")
                st.markdown("The third component gives a visual of the top buyers and sellers of each token. The purpose is to show if a single buyer is "
                            "purchasing more than one and to give an indication of who the big players are in the market.")
            with st.container():
                st.title("Seller To Buyer Web")
                st.markdown("The final component maps the tokens transacted from seller to buyer. The purpose is to see if the "
                            "sellers transact with the  buyers across tokens.")
            st.title("Final Evaluation")
            with st.container():
                st.title("Insight-Based Evaluation")
                st.markdown("I chose to have the user perform an insight base Evaluation for the following reasons:")
                st.markdown("The dashboard is built for data exploration and therefore I need to observe the user to identify what they discover.")
                st.markdown("Holistic evaluation was needed to determine what enhancements needed to be done.")

            with st.container():
                st.title("Final Evaluation Results- Insight Gained – Quotes from the tester")
                st.markdown("It is very easy to see when each project was released compared and the subsequent build up of value in the transactions.")
                st.markdown("Interesting to see the concentration of transactions to few addresses.")
                st.markdown("I wasnt able to see what was happening in the web.")
                st.markdown("Crypto Punks and Bored Apes Yacht Club are trending up in value over time. ")
                st.markdown("People who invested in Crypto Punks Generally did not invest in Bored Apes. However Apes invested in Punks.")

            with st.container():
                st.title("Findings")
                st.markdown("Altair is a very intuitive and useful tool for building graphs and dashboards.")
                st.markdown("Streamlit is a great way to publish Altair graphs in an understandable and intuitive way.")
                st.markdown("The visualization did spark interesting conversations but after the final evaluation it didn’t give the deep insight that I was hoping for. ")
                st.markdown("I would like to add aGraphical model (nodes and edges) but altair does not have one.")
                st.markdown("This project was great and I learned a lot.")

if __name__ == '__main__':
    cd = crypto_dashboard()
    cd.transactions_over_time()
    cd.streamlit_app()
