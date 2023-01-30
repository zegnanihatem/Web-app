import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from streamlit_option_menu import option_menu
from streamlit_login_auth_ui.widgets import __login__



st.set_page_config(
   page_title="Xinlida RFQ system",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)





__login__obj = __login__(auth_token = "courier_auth_token", 
                    company_name = "XINLIDA",
                    width = 200, height = 250, 
                    logout_button_name = 'Logout', hide_menu_bool = False, 
                    hide_footer_bool = False, 
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
    st.image(r"logo.jpeg")
    with st.sidebar:
        menu = option_menu(menu_title="Navigation",options=["Request For Quotation",
        "FMSI Lookup",
        "SHIM Lookup"],
        default_index=1,
        icons=["gear","gear","gear"],

        )
            
    if menu == "Request For Quotation":
        st.markdown("# Request For Quotation")
        Success= RFQ = st.file_uploader("Choose a Request For Quotation")
        if Success:
            RFQ=pd.read_excel(r'SHIM_RFQ.xlsx', skiprows = range(1, 12), usecols = "B:H")
            cols= RFQ.iloc[0].values
            RFQ= RFQ.iloc[1:]
            RFQ.columns= cols
            RFQ= RFQ[RFQ[cols[0]]=="Shim"]
            RFQ['Flat or Tabbed']= RFQ['Flat or Tabbed'].map({'Flat': 'Staked', 'Tabbed': 'Tabbed'})
            st.markdown("## RFQ Data loaded:")
            st.dataframe(RFQ)

            Sheets= pd.read_excel(r"Design1.xlsx", sheet_name=["FMSI", "Kits", "Shim_crossing", "Kit_crossing", "SHIMS"])
            locals().update(Sheets)

            FMSI= FMSI.astype(str)
            Shim_crossing= Shim_crossing.astype(str)

            Flat_SHIMS= FMSI.merge(Shim_crossing, on= 'FMSI').merge(SHIMS, on= 'SHIM PN')
            st.markdown('## Flat SHIMS:')
            st.dataframe(Flat_SHIMS)

            FMSI_matches= RFQ['D Plate Number'].str.extractall(r'(D\d+)')
            FMSI_matches.rename({0: 'FMSI'}, axis= 1, inplace= True)
            FMSI_matches.index.rename(['line', 'match'], inplace= True)
            for i in RFQ.index:
                FMSI_matches.loc[i, 'Flat or Tabbed']= RFQ.loc[i, 'Flat or Tabbed']
            st.markdown('## Extracted FMSI plate numbers: ')
            st.dataframe(FMSI_matches)

            st.markdown('## DataBase lookup (1st group as exemple):')
            
            First_group= FMSI_matches.loc[1, 'FMSI']
            for val in First_group:  #First_group
                Flat_or_tabbed= FMSI_matches[FMSI_matches['FMSI']==val]['Flat or Tabbed'].iloc[0]
                temp_df= Flat_SHIMS[(Flat_SHIMS['FMSI']==val) & (Flat_SHIMS['ATTACHMENT METHOD']==Flat_or_tabbed)]
                temp_df.drop('LINK TYPE', axis= 1).drop_duplicates(inplace= True)
                st.markdown(val)
                st.dataframe(temp_df)
                break

            st.markdown('## Final output:')

            SubResults= []
            for line in FMSI_matches.index.get_level_values('line'):
                line_results=[]
                for match in FMSI_matches.loc[line, 'FMSI']:
                    Flat_or_tabbed= FMSI_matches[FMSI_matches['FMSI']==val]['Flat or Tabbed'].iloc[0]
                    temp_df= Flat_SHIMS[(Flat_SHIMS['FMSI']==match) & (Flat_SHIMS['ATTACHMENT METHOD']==Flat_or_tabbed)]
                    temp_df.drop('LINK TYPE', axis= 1).drop_duplicates(inplace= True)
                    temp_df= Flat_SHIMS[Flat_SHIMS['FMSI']==match]
                    line_results.append(set(temp_df["SHIM PN"].values))
                result= line_results[0].intersection(*line_results)
                Result_df= Flat_SHIMS.loc[(Flat_SHIMS['SHIM PN'].isin(result)) & (Flat_SHIMS['FMSI'].isin(FMSI_matches.loc[line, 'FMSI']))]
                Result_df= Result_df.drop('LINK TYPE', axis= 1).drop_duplicates()
                Result_df['Line']= line
                Result_df.set_index(['Line', 'SHIM PN'], inplace= True)
                SubResults.append(Result_df)
                
            Output= pd.concat(SubResults)
            #Output= Output.drop_duplicates()
            st.dataframe(Output)

            def to_excel(df):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                format1 = workbook.add_format({'num_format': '0.00'}) 
                worksheet.set_column('A:A', None, format1)  
                writer.save()
                processed_data = output.getvalue()
                return processed_data


            df_xlsx = to_excel(Output.reset_index())
            st.download_button(label='📥 Download Current Result',
                                            data=df_xlsx ,
                                            file_name= 'RFQ_output.xlsx')
    if menu == "FMSI Lookup":
        st.markdown("# FMSI Lookup")
        Sheets= pd.read_excel(r"Design1.xlsx", sheet_name=["FMSI", "Kits", "Shim_crossing", "Kit_crossing", "SHIMS"])
        locals().update(Sheets)

        FMSI= FMSI.astype(str)
        Shim_crossing= Shim_crossing.astype(str)

        Flat_SHIMS= FMSI.merge(Shim_crossing, on= 'FMSI').merge(SHIMS, on= 'SHIM PN')        
        FMSI= st.text_input(label= 'FMSI')
        result= Flat_SHIMS[Flat_SHIMS['FMSI'].isin(FMSI.split(', '))]
        st.dataframe(result.set_index(['FMSI', 'SHIM PN', 'LINK TYPE']))
    if menu == "SHIM Lookup":
        st.markdown("# SHIM Lookup")
        Sheets= pd.read_excel(r"Design1.xlsx", sheet_name=["FMSI", "Kits", "Shim_crossing", "Kit_crossing", "SHIMS"])
        locals().update(Sheets)

        FMSI= FMSI.astype(str)
        Shim_crossing= Shim_crossing.astype(str)

        Flat_SHIMS= FMSI.merge(Shim_crossing, on= 'FMSI').merge(SHIMS, on= 'SHIM PN')  
        SHIM= st.text_input(label= 'SHIM')
        result= Flat_SHIMS[Flat_SHIMS['SHIM PN'].isin(SHIM.split(', '))]
        st.dataframe(result.set_index(['SHIM PN', 'FMSI', 'LINK TYPE']))