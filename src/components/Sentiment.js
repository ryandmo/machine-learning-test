import { Component } from 'react';
import { Stack, StackSeparator, Flex } from '@chakra-ui/react';
import { Textarea, InputGroup, CloseButton } from '@chakra-ui/react';
import { IconButton } from "@chakra-ui/react"
import { Spinner, VStack, Text } from "@chakra-ui/react";
import { LuSearch } from "react-icons/lu";
import { Icon } from "@chakra-ui/react";
import { HiHeart } from "react-icons/hi";

// Hover Card
import { Box, HoverCard, Portal, Strong } from "@chakra-ui/react"

// pie chart
import { Chart, useChart } from "@chakra-ui/charts"
import { Cell, LabelList, Pie, PieChart, Tooltip } from "recharts"

const dataURL = 'http://192.168.0.160:8001/sentiment-analysis/';

export default class Sentiment extends Component {
    state = {
        loading: "none",
        question: '',
        chat_conversation_area: []
    };

    getSentimentColor = (sentiment) =>{
        return (sentiment === 'NEG')? "red.400":(sentiment === 'POS') ? "green.400" : "blue.400";
    }

    getChartData = () => {
        const sentimentCount = this.state.chat_conversation_area.reduce((accumulator, current) => {
          const sentiment = current.sentiment;
          accumulator[sentiment] = (accumulator[sentiment] || 0) + 1;
          return accumulator;
        }, {});
        return Object.keys(sentimentCount).map((key, index)=>{
            return {"name": key, "value": sentimentCount[key], "color": this.getSentimentColor(key) }
        })
    }

    Message = (record) => {
        const role = "assistant_role"
        return (
            <Flex
              p={4}
              direction="column"
              className={role}
              bg="gray.200"
              color="black"
              borderRadius="lg"
              w="fit-content"
              alignSelf={role === 'user_role' ? 'flex-end' : 'flex-start'}
            >
                <HoverCard.Root size="sm">
                  <HoverCard.Trigger asChild>
                    <Icon size="lg" color={this.getSentimentColor(record["sentiment"])}>
                        <HiHeart />
                    </Icon>
                  </HoverCard.Trigger>
                  <Portal>
                    <HoverCard.Positioner>
                      <HoverCard.Content maxWidth="240px">
                        <HoverCard.Arrow />
                        <Box>
                          You are feeling <Strong>{ (record["sentiment"] === 'NEG')? "Negative":(record["sentiment"] === 'POS') ? "Positive" : "Neutral" }</Strong>  right now!!
                        </Box>
                      </HoverCard.Content>
                    </HoverCard.Positioner>
                  </Portal>
                </HoverCard.Root>
                 { record["questions"] }
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
                            return this.Message(this.state.chat_conversation_area[key])
                        })}
                    </Stack>
                    <VStack colorPalette="teal" display={this.state.loading}>
                      <Spinner color="colorPalette.600" size="xl"  />
                      <Text color="colorPalette.600">Loading...</Text>
                    </VStack>
                    { this.generateChatInputBox() }
                    <SentimentChart data={ this.getChartData() } />
                </div>
        )
    }

    fetchResponseToTheQuestion = () => {
        this.setState({"loading": "flex"});
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
            this.state.chat_conversation_area.push(data)
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
                    placeholder="Let me help you, with analysing your emotions. Enter how you feel!!"
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


const SentimentChart = (data) => {
    const chart = useChart(data);
    return (
        <Chart.Root boxSize="320px" mx="auto" chart={chart}>
          <PieChart>
            <Tooltip
              cursor={false}
              animationDuration={100}
              content={<Chart.Tooltip hideLabel />}
            />
            <Pie
              isAnimationActive={true}
              data={chart.data}
              dataKey={chart.key("value")}
              outerRadius={100}
              innerRadius={0}
              labelLine={true}
              label={({ name, index }) => {
                const { value } = chart.data[index ?? -1]
                const percent = value / chart.getTotal("value")
                return `${name}: ${(percent * 100).toFixed(1)}%`
              }}
            >
              <LabelList position="inside" fill="white" stroke="none" />
              {chart.data.map((item) => (
                <Cell key={item.questions} fill={chart.color(item.color)} />
              ))}
            </Pie>
          </PieChart>
        </Chart.Root>
    )
}
