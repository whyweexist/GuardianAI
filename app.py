import streamlit as st
import os
import sys
from PIL import Image
from pathlib import Path

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from modules.ip_registration.registration import register_ip
from modules.licensing.license_manager import setup_license_terms
from modules.infringement.detector import check_infringement
from modules.recommendation.recommender import get_recommendations
from modules.dispute.dispute_handler import handle_dispute
from modules.blockchain.web3_utils import connect_wallet, get_account_info

# Set page config
st.set_page_config(
    page_title="Trademark Licensing Platform",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #0E1117;}
    .st-bw {background-color: #1E2126;}
    .css-1d391kg {background-color: #1E2126;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {
        background-color: #1E2126;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button {background-color: #4CAF50; color: white;}
    .stButton>button:hover {background-color: #45a049;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'wallet_connected' not in st.session_state:
    st.session_state.wallet_connected = False
if 'account' not in st.session_state:
    st.session_state.account = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "IP Registration"

# Sidebar for wallet connection
with st.sidebar:
    st.image("https://ipfs.io/ipfs/QmRqYud4pr7gqJTX9YJYmwE9Xy7EkPt4bQz3XgM3NVJrEW", width=200)
    st.title("Trademark Licensing Platform")
    st.markdown("---")
    
    if not st.session_state.wallet_connected:
        st.subheader("Connect Wallet")
        if st.button("Connect with MetaMask"):
            # Simulate wallet connection
            st.session_state.wallet_connected = True
            st.session_state.account = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
            st.experimental_rerun()
    else:
        st.success(f"Connected: {st.session_state.account[:6]}...{st.session_state.account[-4:]}")
        if st.button("Disconnect"):
            st.session_state.wallet_connected = False
            st.session_state.account = None
            st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### Navigation")
    tabs = ["IP Registration", "Licensing", "Infringement Detection", 
            "Recommendations", "Dispute Resolution", "Dashboard"]
    
    for tab in tabs:
        if st.button(tab, key=f"nav_{tab}"):
            st.session_state.active_tab = tab
            st.experimental_rerun()

# Main content
if not st.session_state.wallet_connected:
    st.title("Welcome to the Trademark Licensing Platform")
    st.markdown("""
    ### Connect your wallet to get started
    
    This platform allows you to:
    - Register your intellectual property on-chain
    - Set up programmable licensing terms
    - Detect potential infringements using AI
    - Receive licensing recommendations
    - Handle disputes through arbitration
    
    Click the "Connect with MetaMask" button in the sidebar to begin.
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://ipfs.io/ipfs/QmNtxgPZMUHZJ35yvHnbRNUTVNwniRBhLHQK5zYKiRwxHi", width=200)
    with col2:
        st.image("https://ipfs.io/ipfs/QmPAqZ4EP5joAJpGDFRHhHnpYUfUm1FQKpJ2vgKTdKjHQz", width=200)
    with col3:
        st.image("https://ipfs.io/ipfs/QmRqYud4pr7gqJTX9YJYmwE9Xy7EkPt4bQz3XgM3NVJrEW", width=200)

else:
    # Display content based on active tab
    if st.session_state.active_tab == "IP Registration":
        st.title("IP Registration")
        st.markdown("Register your intellectual property on-chain using Story Protocol")
        
        with st.form("ip_registration_form"):
            asset_name = st.text_input("Asset Name")
            asset_type = st.selectbox("Asset Type", ["Logo", "Name", "Design", "Text", "Other"])
            description = st.text_area("Description")
            uploaded_file = st.file_uploader("Upload Asset", type=["png", "jpg", "jpeg", "svg"])
            
            submitted = st.form_submit_button("Register IP")
            if submitted and uploaded_file is not None:
                # Simulate IP registration process
                st.success(f"Successfully registered {asset_name} on-chain!")
                st.info("IPFS Hash: QmXyZ123...")
                st.info("Transaction Hash: 0xabc123...")
    
    elif st.session_state.active_tab == "Licensing":
        st.title("Licensing Terms Setup")
        st.markdown("Define programmable licensing terms for your intellectual property")
        
        with st.form("licensing_form"):
            st.subheader("Select IP Asset")
            # Simulate list of registered IP assets
            ip_assets = ["Logo - Brand X", "Name - Product Y", "Design - Pattern Z"]
            selected_asset = st.selectbox("Your IP Assets", ip_assets)
            
            st.subheader("License Type")
            license_type = st.selectbox("License Type", ["Open", "Commercial", "Derivative"])
            
            st.subheader("Revenue Split")
            creator_percentage = st.slider("Creator Percentage", 0, 100, 70)
            licensee_percentage = 100 - creator_percentage
            st.info(f"Licensee Percentage: {licensee_percentage}%")
            
            st.subheader("Additional Terms")
            duration = st.selectbox("License Duration", ["1 month", "3 months", "6 months", "1 year", "Perpetual"])
            territory = st.multiselect("Territory", ["Worldwide", "North America", "Europe", "Asia", "Africa", "Australia"])
            
            submitted = st.form_submit_button("Set Up License Terms")
            if submitted:
                st.success("License terms successfully set up!")
                st.info("Smart Contract Address: 0xdef456...")
    
    elif st.session_state.active_tab == "Infringement Detection":
        st.title("Infringement Detection")
        st.markdown("Use AI to detect potential infringements of your intellectual property")
        
        with st.form("infringement_form"):
            st.subheader("Select IP Asset to Monitor")
            # Simulate list of registered IP assets
            ip_assets = ["Logo - Brand X", "Name - Product Y", "Design - Pattern Z"]
            selected_asset = st.selectbox("Your IP Assets", ip_assets)
            
            detection_type = st.multiselect("Detection Methods", ["Image Similarity (CLIP)", "Text Matching (OCR)", "Web Crawling"])
            threshold = st.slider("Similarity Threshold (%)", 50, 100, 75)
            
            submitted = st.form_submit_button("Start Detection")
            if submitted:
                # Simulate detection results
                st.success("Detection completed!")
                
                st.subheader("Detection Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### Potential Infringement #1")
                    st.image("https://ipfs.io/ipfs/QmNtxgPZMUHZJ35yvHnbRNUTVNwniRBhLHQK5zYKiRwxHi", width=150)
                    st.markdown("**Similarity Score:** 87%")
                    st.markdown("**Source:** example.com/logo")
                    if st.button("Take Action", key="action1"):
                        st.session_state.active_tab = "Recommendations"
                        st.experimental_rerun()
                
                with col2:
                    st.markdown("### Potential Infringement #2")
                    st.image("https://ipfs.io/ipfs/QmPAqZ4EP5joAJpGDFRHhHnpYUfUm1FQKpJ2vgKTdKjHQz", width=150)
                    st.markdown("**Similarity Score:** 79%")
                    st.markdown("**Source:** anothersite.org/brand")
                    if st.button("Take Action", key="action2"):
                        st.session_state.active_tab = "Recommendations"
                        st.experimental_rerun()
    
    elif st.session_state.active_tab == "Recommendations":
        st.title("Licensing Recommendations")
        st.markdown("Get recommendations for handling potential infringements")
        
        # Simulate infringement case
        st.subheader("Infringement Case")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Your IP Asset")
            st.image("https://ipfs.io/ipfs/QmNtxgPZMUHZJ35yvHnbRNUTVNwniRBhLHQK5zYKiRwxHi", width=200)
            st.markdown("**Asset Name:** Logo - Brand X")
            st.markdown("**Registration Date:** 2023-05-15")
        
        with col2:
            st.markdown("### Detected Infringement")
            st.image("https://ipfs.io/ipfs/QmPAqZ4EP5joAJpGDFRHhHnpYUfUm1FQKpJ2vgKTdKjHQz", width=200)
            st.markdown("**Similarity Score:** 87%")
            st.markdown("**Source:** example.com/logo")
            st.markdown("**Detection Date:** 2023-06-10")
        
        st.markdown("---")
        st.subheader("Recommended Actions")
        
        tab1, tab2 = st.tabs(["License Offer", "Takedown Notice"])
        
        with tab1:
            st.markdown("### Proposed License Terms")
            st.markdown("Based on your pre-set terms, we recommend offering the following license:")
            st.markdown("- **License Type:** Commercial")
            st.markdown("- **Duration:** 1 year")
            st.markdown("- **Revenue Split:** 70% Creator / 30% Licensee")
            st.markdown("- **Territory:** Worldwide")
            
            if st.button("Generate License Contract"):
                st.success("License contract generated!")
                st.code("""
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@storyprotocol/contracts/IPLicense.sol";

contract TrademarkLicense {
    address public licensor;
    address public licensee;
    uint256 public assetId;
    uint256 public royaltyPercentage;
    uint256 public duration;
    
    // License terms and conditions...
}
                """, language="solidity")
                
                if st.button("Send Offer"):
                    st.success("License offer sent to potential infringer!")
        
        with tab2:
            st.markdown("### Takedown Notice Template")
            st.markdown("If you prefer to issue a takedown notice instead of offering a license:")
            
            takedown_notice = """
[Your Company Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]

[Date]

[Recipient Name]
[Recipient Address]
[City, State ZIP]

Re: Copyright/Trademark Infringement Notice

To Whom It May Concern:

I am writing to notify you that your website/business is infringing on my intellectual property rights. I own the trademark/copyright to [Asset Name], which appears on your website/business at [URL/Location].

Under the Digital Millennium Copyright Act (DMCA) and trademark law, I am requesting the immediate removal of the infringing material.

I have a good faith belief that the use of the material in the manner complained of is not authorized by me, the copyright/trademark owner.

Please respond within 10 business days to confirm you have removed the infringing content.

Sincerely,
[Your Name]
            """
            
            st.text_area("Customize Notice", takedown_notice, height=300)
            if st.button("Send Takedown Notice"):
                st.success("Takedown notice sent to potential infringer!")
    
    elif st.session_state.active_tab == "Dispute Resolution":
        st.title("Dispute Resolution")
        st.markdown("Handle disputes through DAO or arbiter-based mechanisms")
        
        # Simulate active disputes
        st.subheader("Active Disputes")
        
        with st.expander("Dispute #1: Logo Infringement - Brand X vs. Company Y"):
            st.markdown("**Status:** Pending Arbitration")
            st.markdown("**Filed Date:** 2023-06-15")
            st.markdown("**Description:** Company Y is using a logo that is 87% similar to Brand X's registered trademark.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Original IP")
                st.image("https://ipfs.io/ipfs/QmNtxgPZMUHZJ35yvHnbRNUTVNwniRBhLHQK5zYKiRwxHi", width=150)
            with col2:
                st.markdown("### Alleged Infringement")
                st.image("https://ipfs.io/ipfs/QmPAqZ4EP5joAJpGDFRHhHnpYUfUm1FQKpJ2vgKTdKjHQz", width=150)
            
            st.markdown("### Arbitration Options")
            arbitration_method = st.radio("Select Arbitration Method", ["DAO Voting", "Single Arbiter", "Panel of Experts"])
            
            if arbitration_method == "DAO Voting":
                st.markdown("DAO members will vote on the resolution of this dispute.")
                if st.button("Initiate DAO Vote"):
                    st.success("DAO voting initiated! Members have 7 days to cast their votes.")
            
            elif arbitration_method == "Single Arbiter":
                arbiters = ["John Doe (IP Specialist)", "Jane Smith (Trademark Attorney)", "Alex Johnson (Blockchain Expert)"]
                selected_arbiter = st.selectbox("Select Arbiter", arbiters)
                if st.button("Appoint Arbiter"):
                    st.success(f"{selected_arbiter} has been appointed as the arbiter for this dispute.")
            
            elif arbitration_method == "Panel of Experts":
                st.markdown("A panel of 3 experts will review the case and make a decision.")
                if st.button("Convene Expert Panel"):
                    st.success("Expert panel has been convened. You will be notified when they reach a decision.")
        
        with st.expander("Dispute #2: Name Usage - Product Y vs. Service Z"):
            st.markdown("**Status:** In Settlement Negotiation")
            st.markdown("**Filed Date:** 2023-05-20")
            st.markdown("**Description:** Service Z is using a name that is confusingly similar to Product Y's registered trademark.")
            
            st.markdown("### Settlement Proposal")
            st.markdown("Service Z has proposed the following settlement:")
            st.markdown("- Rebranding within 60 days")
            st.markdown("- One-time payment of 2 ETH")
            st.markdown("- Public acknowledgment of Product Y's trademark rights")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Accept Settlement"):
                    st.success("Settlement accepted! Smart contract will be generated to enforce terms.")
            with col2:
                if st.button("Reject & Continue Dispute"):
                    st.error("Settlement rejected. Dispute will proceed to formal arbitration.")
    
    elif st.session_state.active_tab == "Dashboard":
        st.title("IP Portfolio Dashboard")
        
        # IP Assets Overview
        st.subheader("Your IP Assets")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Registered IP Assets", "3")
        with col2:
            st.metric("Active Licenses", "2")
        with col3:
            st.metric("Pending Disputes", "1")
        
        # IP Assets Table
        st.markdown("### Registered IP Assets")
        ip_data = {
            "Asset Name": ["Logo - Brand X", "Name - Product Y", "Design - Pattern Z"],
            "Type": ["Logo", "Name", "Design"],
            "Registration Date": ["2023-05-15", "2023-04-22", "2023-06-01"],
            "IPFS Hash": ["QmXyZ123...", "QmAbc456...", "QmDef789..."],
            "Status": ["Active", "Active", "Active"]
        }
        st.dataframe(ip_data)
        
        # Licensing Activity
        st.markdown("### Licensing Activity")
        license_data = {
            "Licensee": ["Company A", "Individual B"],
            "Asset": ["Logo - Brand X", "Design - Pattern Z"],
            "Type": ["Commercial", "Derivative"],
            "Start Date": ["2023-05-20", "2023-06-10"],
            "End Date": ["2024-05-20", "2023-12-10"],
            "Revenue": ["0.5 ETH", "0.2 ETH"]
        }
        st.dataframe(license_data)
        
        # Infringement Alerts
        st.markdown("### Recent Infringement Alerts")
        alert_data = {
            "Asset": ["Logo - Brand X", "Name - Product Y"],
            "Similarity": ["87%", "92%"],
            "Source": ["example.com/logo", "anothersite.org/brand"],
            "Detection Date": ["2023-06-10", "2023-06-08"],
            "Status": ["Action Pending", "License Offered"]
        }
        st.dataframe(alert_data)
        
        # Analytics
        st.subheader("Analytics")
        chart_data = {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Infringements": [1, 0, 2, 1, 3, 2],
            "Licenses": [0, 1, 0, 1, 0, 2],
            "Revenue (ETH)": [0, 0.2, 0, 0.3, 0, 0.7]
        }
        
        tab1, tab2 = st.tabs(["Infringement & Licensing", "Revenue"])
        with tab1:
            st.bar_chart({"Infringements": chart_data["Infringements"], "Licenses": chart_data["Licenses"]}, x=chart_data["Month"])
        with tab2:
            st.line_chart({"Revenue (ETH)": chart_data["Revenue (ETH)"]}, x=chart_data["Month"])

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>© 2023 Trademark Licensing Platform | Powered by Story Protocol</p>
</div>
""", unsafe_allow_html=True)