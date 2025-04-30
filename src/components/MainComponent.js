import { Component } from 'react';
import { Heading } from "@chakra-ui/react";
import { Tabs } from '@chakra-ui/react';
import Chatbot from "./Chatbot";
import Sentiment from './Sentiment';
import ImageCaptioning from './ImageCaptioning';

export default class MainComponent extends Component {
    state = {
    };

generateTabPanel = () => {
        const tabs = {
            "AI Assistance": <Chatbot />,
            "Sentiment Analysis": <Sentiment />,
            "Image Captioning": <ImageCaptioning />
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
                        return (<Tabs.Content value={tabName}>
                            { tabs[tabName] }
                        </Tabs.Content>)
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
