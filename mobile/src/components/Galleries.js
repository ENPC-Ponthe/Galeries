import {ImageListContainer, ImageSource} from 'react-native-interactive-image-gallery'
import React, {PureComponent} from 'react';
import {ActivityIndicator, View} from 'react-native';
import {url, get} from "../services/HttpClient";
import PropTypes from "prop-types";

export default class Galleries extends PureComponent<Props> {
    static childContextTypes = {
        onSourceContext: PropTypes.func.isRequired
    }

    constructor(props) {
        super(props)
        this.state ={
            isLoading: true,
        }

        this._imageMeasurers = {}
        this._imageSizeMeasurers = {}
    }

    getChildContext() {
        return { onSourceContext: this._onSourceContext }
    }

    _onSourceContext = (
        imageId: string,
        cellMeasurer: Function,
        imageMeasurer: Function
    ) => {
        this._imageMeasurers[imageId] = cellMeasurer
        this._imageSizeMeasurers[imageId] = imageMeasurer
    }

    onFetch = (data) => {
        this.setState({
            isLoading: false,
            data,
        })
    }

    async componentDidMount(){
        await get('/galleries', this.onFetch)
    }

    render() {
        if(this.state.isLoading){
            return(
                <View style={{flex: 1, padding: 20}}>
                    <ActivityIndicator/>
                </View>
            )
        }

        const imageURLs: Array<ImageSource> = this.state.data.map(
            (gallery: Object, index: number) => ({
                URI: url(gallery.cover_uri),
                thumbnail: url(gallery.cover_uri),
                id: gallery.slug,
                overlayText: gallery.name,
            })
        )

        const { navigate } = this.props.navigation
        return <ImageListContainer images={imageURLs}
                                   onPressImage={(imageId) => navigate('Gallery', { gallery_slug: imageId })}
                                   displayImageViewer={false}
                                   topMargin={0} />
    }
}