css = '''
<style>
    body {
        font-family: 'monospace', sans-serif;
        background-color: #FFFFFF;
    }

    .chat-message {
        display: flex;
        align-items: center;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .chat-message.user {
        background-color: #f6def2;
        justify-content: flex-end;
    }

    .chat-message.bot {
        background-color: #C1A0E8;
    }

    .chat-message .message {
        width: 80%;
        padding: 0 1.5rem;
        color: #916DB3;
        background-color: #FFFFFF;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    .chat-message.user .message {
        order: 1;
    }

    .chat-message.bot .message {
        order: 1;
    }
</style>

'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG}}</div>
</div>
<script>
    async function displayTextWithTypingAnimation(text, speed) {
        console.log(text)
        for (const char of text) {
            document.getElementById('chat-box').innerText += char;
            await new Promise(resolve => setTimeout(resolve, speed)); // Delay between characters
        }
    }

    const generatedText = "";
    const typingSpeed = 50; // Adjust the speed (in milliseconds) between characters
    console.log(generatedText)
    displayTextWithTypingAnimation(generatedText, typingSpeed);
</script>

'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>

'''

img_template='''
<div class="centered-image">
    <img src="{{img}}" style="display: block; margin: 0 auto;">
</div>

'''
