import os
css = '''
<style>
.chat-message {
    text-decoration: none !important;
    padding: 0.6rem;  /* Reduced from 1.5rem */
    border-radius: 0.9rem;  /* Slightly smaller radius */
    margin-bottom: 0.6rem;  /* Reduced spacing between messages */
    display: flex;
    font-size: 0.rem;  /* Slightly smaller font */
}
.chat-message.user {
    background-color: #2b313e;
    margin-left: 15%;  /* Reduced from 20% */
    border-bottom-right-radius: 0;
}
.chat-message.bot {
    background-color: #475063;
    margin-right: 15%;  /* Reduced from 20% */
    border-bottom-left-radius: 0;
}
.chat-message .avatar {
  width: 10%;  /* Reduced from 20% */
}
.chat-message .avatar img {
  max-width: 30px;  /* Reduced from 30px */
  max-height: 30px;  /* Reduced from 30px */
  border-radius: 70%;
  object-fit: cover;
}
.chat-message .message {
  width: 90%;  /* Increased from 80% to compensate for smaller avatar */
  padding: 0 0.8rem;  /* Reduced from 1.5rem */
  color: #fff;
  line-height: 1.3;  /* Tighter line spacing */
}
.input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 0.6rem;  /* Reduced from 1rem */
    background-color: #1a1c24;
    z-index: 100;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}
.stTextInput>div>div>input {
    color: white;
    background-color: #2b313e;
    font-size: 0.9rem;  /* Match the message font size */
    padding: 0.5rem;  /* Smaller input padding */
}
</style>
'''

def get_bot_template(MSG):
    MSG = MSG.replace("[INST]", "").replace("[/INST]", "").replace("<s>", "").replace("</s>", "")
    
    bot_template = f'''
    <div class="chat-message bot">
        <div class="avatar">
            <img src="https://media.istockphoto.com/id/2074604864/vector/chatbot-smiley-robot-face-icon-with-microphone-and-speech-bubble-vector-thin-line.jpg?s=612x612&w=0&k=20&c=MrqadmP-Eq3o7bXHN4WPbv1v8jrwOyS72O6fNcuNqZw=" 
                 style="max-height: 24px; max-width: 24px; border-radius: 50%; object-fit: cover;">
        </div>
        <div class="message">{MSG}</div>
    </div>
    '''
    return bot_template

def get_user_template(MSG):
    if os.path.exists("image.txt"):
        with open("image.txt", "r") as f:
            img_src = f.read()
    else:
        img_src = "https://cdn-icons-png.flaticon.com/512/8815/8815112.png"
        
    user_template = f'''
    <div class="chat-message user">
        <div class="message">{MSG}</div>
        <div class="avatar">
            <img src="{img_src}" 
                 style="max-height: 24px; max-width: 24px; border-radius: 50%; object-fit: cover;">
        </div>    
    </div>
    '''
    return user_template