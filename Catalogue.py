import streamlit as st
import pandas as pd
import numpy as np
import streamlit_authenticator as stauth

import streamlit as st
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
    st.image(r'C:\Users\AHMED Raja\Desktop\XINLIDA\Web app\logo2.png')
    st.markdown("# Welcome to XINLIDA Catalogue")

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
        st.markdown('## Extracted FMSI plate numbers: ')
        st.dataframe(FMSI_matches)

        st.markdown('## DataBase lookup (1st group as exemple):')
        First_group= FMSI_matches.loc[1][0]

        
        for val in FMSI_matches.loc[1][0]:  #Column 0
            temp_df= Flat_SHIMS[Flat_SHIMS['FMSI']==val]
            st.markdown(val)
            st.dataframe(temp_df)

        st.markdown('## 1st common group:')

        result= set(temp_df["SHIM PN"].values)
        for val in FMSI_matches.loc[1][0]:  #Column 0
            temp_df= Flat_SHIMS[Flat_SHIMS['FMSI']==val]
            result= result.intersection(set(temp_df["SHIM PN"].values))
        Result_df= Flat_SHIMS.loc[Flat_SHIMS['SHIM PN'].isin(result) ]
        st.dataframe(Result_df.set_index('SHIM PN'))

 