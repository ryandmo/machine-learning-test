import { Component } from 'react';
import { Image, HStack, Stack } from "@chakra-ui/react";
import { Button, FileUpload } from "@chakra-ui/react";
import { Field, Fieldset } from "@chakra-ui/react";
import { HiUpload } from "react-icons/hi";
import { Tag } from "@chakra-ui/react";

const dataURL = 'http://192.168.0.160:8002/generate-caption-for-image/';
const fetchImageURL = 'http://192.168.0.160:8002/get-image/';
const historyURL = 'http://192.168.0.160:8002/fetch-image-caption-history/';

export default class ImageCaptioning extends Component {
    state = {
        loading: "none",
        gallery_history: [],
        fileUpload: undefined,
        history_button_loading: false,
        caption_button_loading: false
    };

    showGallery = () => {
        return (
            <HStack
            spacing={4} overflowX="auto" flex={1}
            >
                {Object.keys(this.state.gallery_history).map((key, index) => {
                    return this.generateThumbnail(this.state.gallery_history[key])
                })}
            </HStack>
        )
    }

    fetchHistory = () => {
        this.setState({"loading": "flex"});
        this.setState({"history_button_loading": true});
        fetch(historyURL, {
            mode: 'cors'
        })
        .then(response => response.json())
        .then(data => {
            this.setState({"gallery_history": data});
            this.setState({"loading": "none"});
            this.setState({"history_button_loading": false});
        })
        .catch(err => {
            console.log(err)
            this.setState({"loading": "none"});
            this.setState({"history_button_loading": false});
        });
    }

    generateCaption = () => {
        this.setState({"loading": "flex"});
        this.setState({"caption_button_loading": true});
        var data = new FormData();
        data.append('User', "Ryan");
        try{
            data.append( "input_file", this.state.fileUpload[0]);
        }catch(e){
            alert("Please Upload a file to generate caption.");
            return;
        }

        fetch(dataURL, {
            mode: 'cors',
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            this.state.gallery_history.push(data);
            this.setState({"loading": "none"});
            this.setState({"caption_button_loading": false});
        })
        .catch(err => {
            console.log(err)
            this.setState({"loading": "none"});
            this.setState({"caption_button_loading": false});
        });
    }

    generateImageUploadArea = () => {
        return (
        <Stack align="flex-start" h="600px">
            <Fieldset.Root colorPalette="teal" w="600px">
                <Fieldset.Legend>Create Gallery ith Captions:</Fieldset.Legend>
                <Fieldset.Content>
                    <Field.Root>
                        <FileUpload.Root onFileChange={(details)=>{ this.setState({"fileUpload": details["acceptedFiles"]})} } accept={["image/png", "image/jpg", "image/jpeg"]}>
                              <FileUpload.HiddenInput />
                              <FileUpload.Trigger asChild>
                                <Button variant="outline" size="sm">
                                  <HiUpload /> Choose image for generating Captions.
                                </Button>
                              </FileUpload.Trigger>
                              <FileUpload.List />
                        </FileUpload.Root>
                    </Field.Root>
                </Fieldset.Content>
                <HStack>
                    <Button w="200px" type="submit" loading={ this.state.caption_button_loading } onClick={ event => { this.generateCaption() }} loadingText="Loading" spinnerPlacement="start">
                        Generate Caption
                    </Button>
                    <Button w="200px" loading={ this.state.history_button_loading } onClick={ event => { this.fetchHistory() }} loadingText="Loading" spinnerPlacement="start">
                        Show Gallery
                    </Button>
                </HStack>
            </Fieldset.Root>
            { this.showGallery() }
          </Stack>
          )
    }

    generateThumbnail = (record) => {
        const ImageURL = `${fetchImageURL}?filename=${record["questions"]}`;
        return (
            <Stack flexShrink="0">
                <Image id={ record["_id"] }
                    src={ImageURL}
                    width="300px"
                />
                <Tag.Root>
                    <Tag.Label>{ record["generated_text"] }</Tag.Label>
                </Tag.Root>
            </Stack>
        )
    }

    // Gallery will be HStack of Image
    render() {
        return this.generateImageUploadArea();
    }
}