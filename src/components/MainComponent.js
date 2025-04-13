import { Component } from 'react';
import { Heading } from "@chakra-ui/react";
import Chatbot from "./Chatbot";

export default class MainComponent extends Component {
    state = {
    };

    render() {
        return (
            <div>
                <br />
                <title>Learning project with AI integration!!</title>
                <br />
                <Heading>Learning project with AI integration!!</Heading>
                 <Chatbot / >
            </div>
        )
    }
}
