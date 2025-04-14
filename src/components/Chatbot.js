import { Component } from 'react';
import { Tabs } from '@chakra-ui/react';
import { Stack, StackSeparator } from '@chakra-ui/react';
import { Input, InputGroup, CloseButton } from '@chakra-ui/react';
import { IconButton } from "@chakra-ui/react"
import { LuSearch } from "react-icons/lu"
import Markdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

const generateChatConversationURL = 'http://192.168.0.160:8001/get_assistance/';

export default class Chatbot extends Component {
    state = {
        question_limit: 5,
        loading: false,
        question: '',
        chat_conversation_area: <Stack gap="4" separator={<StackSeparator />} ><div className="assistant_role"><p>How Can I help you??</p></div></Stack>
    };

    handleQuestionLimit = () => {
        if(this.state.question_limit <= 0){
            return false;
        }
        this.setState({
            question_limit: this.state.question_limit - 1
        })
        return true;
    };

    generateTabPanel = () => {
        const tabs = {
            "chatbot": "Chatbot responses",
            "two": "Second!",
            "three": "Third!"
        };
        return (
            <div>
                <Tabs.Root>
                    <Tabs.List>
                        {Object.keys(tabs).map((tabName, TabIndex) =>{
                            return <Tabs.Trigger value={tabName} >{tabName}</Tabs.Trigger>;
                        })}
                    </Tabs.List>
                    {Object.keys(tabs).map((tabName, TabIndex) =>{
                        if(tabName === "chatbot"){
                             return (<Tabs.Content value={tabName}>
                                { this.state.chat_conversation_area }
                                <Stack separator={<StackSeparator />} >&nbsp;</Stack>
                                { this.generateChatInputBox() }
                             </Tabs.Content>);
                        }else{
                            return (<Tabs.Content value={tabName}>
                                <p> {tabs[tabName]} </p>
                            </Tabs.Content>)
                        }
                    })}
                </Tabs.Root>
            </div>
        )
    }

    generateChatConversationArea = (data) => {
        return (
            <Stack gap="4" separator={<StackSeparator />} >
                    <div className="assistant_role">
                        <Markdown rehypePlugins={[rehypeRaw]}>
                            {data}
                        </Markdown>
                    </div>
            </Stack>
        );
    }

    fetchResponseToTheQuestion = () => {
        this.setState({"loading": true});
        var data = new FormData();
        data.append( "json", JSON.stringify({
            "questions": [this.state.question]
        }));
        fetch(generateChatConversationURL, {
            mode: 'cors',
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            this.setState({'chat_conversation_area': this.generateChatConversationArea(data[0])})
            this.setState({"loading": false})
            this.setState({"question": ''})
        })
        .catch(err => {
            console.log(err)
            this.setState({"loading": false})
        });
    }

    generateChatInputBox = () => {
         const clearButton = this.state.question ? (
            <CloseButton
              size="xs"
              onClick={
                event => {this.setState({question: ''})}
              }
              me="-2"
            />
          ) : undefined

          const submitButton = this.state.question ? (
            <IconButton aria-label="Ask AI Questions." onClick={ event => {this.fetchResponseToTheQuestion()} }>
              <LuSearch />
            </IconButton>
          ) : undefined

        return (
            <InputGroup endElement=<div>{ clearButton }<span>&nbsp;</span>{ submitButton }</div> >
                <Input
                    variant='subtle'
                    placeholder="Welcome to AI assistance. How can I help you?"
                    value = {this.state.question}
                    onChange={event => {this.setState({question: event.target.value})}}
                    onKeyPress={event => {
                        if (event.key === 'Enter') {
                            this.fetchResponseToTheQuestion()
                        }
                    }}
                />
            </InputGroup>
        )
    }

    render() {
        return this.generateTabPanel()
    }
}