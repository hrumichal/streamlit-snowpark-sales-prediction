import streamlit as st
import streamlit.components.v1 as components

def setUI():
    hvar='''
        <script>
             setTimeout(()=>{
                toHide=window.parent.document.querySelectorAll('iframe[height="0"]')
                for (const iframe of toHide) {
                    if(iframe.hasAttribute("srcdoc"))
                        iframe.parentElement.style.display="none"
                }
            },300)
            var my_style= window.parent.document.createElement('style');
            my_style.innerHTML=`
                
                .stApp header{
                    /* display:none;*/
                     display:none;
                }
                div[data-testid="stVerticalBlock"] {
                    gap:0.6rem;
                }
                .main .block-container{
                    max-width: unset;
                    padding-left:0em;
                    padding-right: 0em;
                    padding-top: 0em;
                    padding-bottom: 1em;
                    }
            `;
            window.parent.document.head.appendChild(my_style);       
        </script>
        '''
    components.html(hvar, height=0, width=0)
