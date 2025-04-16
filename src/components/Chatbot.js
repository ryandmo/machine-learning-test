import { Component } from 'react';
import { Tabs } from '@chakra-ui/react';
import { Stack, StackSeparator, Flex } from '@chakra-ui/react';
import { Input, InputGroup, CloseButton } from '@chakra-ui/react';
import { IconButton } from "@chakra-ui/react"
import { Spinner, VStack, Text } from "@chakra-ui/react";
import { LuSearch } from "react-icons/lu"
import Markdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

const generateChatConversationURL = 'http://192.168.0.160:8001/get_assistance/';

export default class Chatbot extends Component {
    state = {
        question_limit: 5,
        loading: "none",
        question: '',
        chat_conversation_area: []
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

    Message = (text, role) => {
        return (
            <Flex
              p={4}
              direction="column"
              className={role}
              bg={role === 'user_role' ? 'blue.500' : 'gray.200'}
              color={role === 'user_role' ? 'white' : 'black'}
              borderRadius="lg"
              w="fit-content"
              alignSelf={role === 'user_role' ? 'flex-end' : 'flex-start'}
            >
                <Markdown rehypePlugins={[rehypeRaw]}>
                    { text }
                </Markdown>
            </Flex>
         )
    }

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
                                <Stack
                                gap="4" separator={<StackSeparator />}
                                px={4} py={10} overflow="auto" flex={1}
                                css={{
                                    '&::-webkit-scrollbar': {
                                      width: '4px',
                                    },
                                    '&::-webkit-scrollbar-track': {
                                      width: '6px',
                                    },
                                    '&::-webkit-scrollbar-thumb': {
                                      background: '#d5e3f7',
                                      borderRadius: '24px',
                                    },
                                  }}
                                >
                                    {Object.keys(this.state.chat_conversation_area).map((key, index)=>{
                                        if(key%2 === 0){
                                            return this.Message(this.state.chat_conversation_area[key], "user_role")
                                        }else{
                                            return this.Message(this.state.chat_conversation_area[key], "assistant_role")
                                        }

                                    })}
                                </Stack>
                                <VStack colorPalette="teal" display={this.state.loading}>
                                  <Spinner color="colorPalette.600" size="xl"  />
                                  <Text color="colorPalette.600">Loading...</Text>
                                </VStack>
                                { this.generateChatInputBox() }
                             </Tabs.Content>)
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

    fetchResponseToTheQuestion = () => {
        this.setState({"loading": "flex"});
        // Add the user question also to the chat history
        if (this.state.question !== ''){
            this.state.chat_conversation_area.push(this.state.question);
        }
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
            this.state.chat_conversation_area.push(data[0])
            this.setState({"loading": "none"});
            this.setState({"question": ''})
        })
        .catch(err => {
            console.log(err)
            this.setState({"loading": "none"});
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