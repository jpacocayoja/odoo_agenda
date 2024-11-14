/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

class AudioRecorderField extends Component {
  static template = "mi_modulo_academico.AudioRecorderField";

  static props = {
    ...standardFieldProps,
  };

  setup() {
    this.state = useState({
      isRecording: false,
      audioURL: null,
      mediaRecorder: null,
      audioChunks: [],
    });

    if (this.props.value) {
      this.state.audioURL = `data:audio/wav;base64,${this.props.value}`;
    }

    this.initializeRecorder();
  }

  async initializeRecorder() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 44100,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      this.state.mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      this.state.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.state.audioChunks.push(event.data);
        }
      };

      this.state.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.state.audioChunks, {
          type: "audio/webm",
        });

        if (this.state.audioURL) {
          URL.revokeObjectURL(this.state.audioURL);
        }

        // Convertir el audio usando AudioContext
        const audioContext = new (window.AudioContext ||
          window.webkitAudioContext)({
          sampleRate: 44100,
        });

        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // Crear un nuevo buffer con la configuración correcta
        const offlineCtx = new OfflineAudioContext({
          numberOfChannels: 1,
          length: audioBuffer.duration * 44100,
          sampleRate: 44100,
        });

        const source = offlineCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(offlineCtx.destination);
        source.start();

        const renderedBuffer = await offlineCtx.startRendering();
        const wavBlob = this.bufferToWav(renderedBuffer);

        this.state.audioURL = URL.createObjectURL(wavBlob);

        // Convertir a base64
        const reader = new FileReader();
        reader.readAsDataURL(wavBlob);
        reader.onloadend = () => {
          const base64data = reader.result.split(",")[1];
          this.props.record.update({
            [this.props.name]: base64data,
            [`${this.props.name}_nombre`]: "recorded_audio.wav",
          });
        };
      };
    } catch (error) {
      console.error("Error initializing audio recorder:", error);
    }
  }

  bufferToWav(audioBuffer) {
    const numChannels = 1; // Forzar mono
    const sampleRate = 44100; // Frecuencia de muestreo estándar
    const format = 1; // PCM
    const bitDepth = 16; // Profundidad de bits

    const length = audioBuffer.length * numChannels * (bitDepth / 8);
    const buffer = new ArrayBuffer(44 + length);
    const view = new DataView(buffer);
    const channelData = audioBuffer.getChannelData(0);

    /* Write WAV header */
    const writeString = (view, offset, string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(view, 0, "RIFF");
    view.setUint32(4, 36 + length, true);
    writeString(view, 8, "WAVE");
    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
    view.setUint16(32, numChannels * (bitDepth / 8), true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, "data");
    view.setUint32(40, length, true);

    // Write audio data
    const volume = 0.8;
    let offset = 44;
    for (let i = 0; i < channelData.length; i++) {
      const sample = Math.max(-1, Math.min(1, channelData[i])) * volume;
      view.setInt16(
        offset,
        sample < 0 ? sample * 0x8000 : sample * 0x7fff,
        true
      );
      offset += 2;
    }

    return new Blob([buffer], { type: "audio/wav" });
  }

  startRecording() {
    if (this.state.mediaRecorder && !this.state.isRecording) {
      this.state.audioChunks = [];
      try {
        this.state.mediaRecorder.start();
        this.state.isRecording = true;
      } catch (e) {
        console.error("Error starting recording:", e);
      }
    }
  }

  stopRecording() {
    if (this.state.mediaRecorder && this.state.isRecording) {
      try {
        this.state.mediaRecorder.stop();
        this.state.isRecording = false;
      } catch (e) {
        console.error("Error stopping recording:", e);
      }
    }
  }

  deleteRecording() {
    if (this.state.audioURL) {
      URL.revokeObjectURL(this.state.audioURL);
      this.state.audioURL = null;
      this.state.audioChunks = [];
      this.props.record.update({
        [this.props.name]: false,
        [`${this.props.name}_nombre`]: false,
      });
    }
  }
}

export const audioRecorderField = {
  component: AudioRecorderField,
  supportedTypes: ["binary"],
  extractProps: ({ attrs, field }) => ({
    name: field.name,
  }),
};

registry.category("fields").add("audio_recorder", audioRecorderField);
