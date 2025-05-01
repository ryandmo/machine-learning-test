import { Component } from 'react';
import { Stack, StackSeparator, Flex } from '@chakra-ui/react';
import { Textarea, InputGroup, CloseButton } from '@chakra-ui/react';
import { IconButton } from "@chakra-ui/react"
import { Spinner, VStack, Text } from "@chakra-ui/react";
import { LuSearch } from "react-icons/lu"
import Markdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

const dataURL = 'http://192.168.0.160:8002/get_assistance/';

export default class Chatbot extends Component {
    state = {
        loading: "none",
        question: '',
        chat_conversation_area: []
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

    generateConversationArea = () => {
        return (
                <div>
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
        fetch(dataURL, {
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
                <Textarea
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
        return this.generateConversationArea()
    }
}