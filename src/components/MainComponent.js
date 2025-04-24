import { Component } from 'react';
import { Heading } from "@chakra-ui/react";
import { Tabs } from '@chakra-ui/react';
import Chatbot from "./Chatbot";
import Sentiment from './Sentiment';

export default class MainComponent extends Component {
    state = {
    };

generateTabPanel = () => {
        const tabs = {
            "chatbot": "Chatbot responses",
            "sentiment analysis": "Second!",
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
                            return (<Tabs.Content value="chatbot">
                                <Chatbot />
                            </Tabs.Content>)
                        }else if(tabName === "sentiment analysis"){
                           return (<Tabs.Content value={tabName}>
                               <Sentiment />
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
    render() {
        return (
            <div>
                <br />
                <title>Learning project with AI integration!!</title>
                <br />
                <Heading>Learning project with AI integration!!</Heading>
                 { this.generateTabPanel() }
            </div>
        )
    }
}
