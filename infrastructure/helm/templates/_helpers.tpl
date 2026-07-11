{{/*
==============================================================================
Institutional Quant Platform
Helm Helper Templates
==============================================================================
*/}}

{{/*
Expand chart name.
*/}}
{{- define "institutional-quant.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{/*
Create fully qualified application name.
*/}}
{{- define "institutional-quant.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "institutional-quant.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Chart name and version.
*/}}
{{- define "institutional-quant.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end }}

{{/*
==============================================================================
Common Labels
==============================================================================
*/}}

{{- define "institutional-quant.labels" -}}

helm.sh/chart: {{ include "institutional-quant.chart" . }}

app.kubernetes.io/name: {{ include "institutional-quant.name" . }}

app.kubernetes.io/instance: {{ .Release.Name }}

app.kubernetes.io/version: "{{ .Chart.AppVersion }}"

app.kubernetes.io/managed-by: {{ .Release.Service }}

{{- end }}

{{/*
==============================================================================
Selector Labels
==============================================================================
*/}}

{{- define "institutional-quant.selectorLabels" -}}

app.kubernetes.io/name: {{ include "institutional-quant.name" . }}

app.kubernetes.io/instance: {{ .Release.Name }}

{{- end }}

{{/*
==============================================================================
Namespace
==============================================================================
*/}}

{{- define "institutional-quant.namespace" -}}

{{- default .Release.Namespace .Values.global.namespace }}

{{- end }}

{{/*
==============================================================================
API Image
==============================================================================
*/}}

{{- define "institutional-quant.apiImage" -}}

{{ printf "%s/%s:%s" .Values.global.imageRegistry .Values.images.api.repository .Values.images.api.tag }}

{{- end }}

{{/*
==============================================================================
Analytics Image
==============================================================================
*/}}

{{- define "institutional-quant.analyticsImage" -}}

{{ printf "%s/%s:%s" .Values.global.imageRegistry .Values.images.analytics.repository .Values.images.analytics.tag }}

{{- end }}

{{/*
==============================================================================
Dashboard Image
==============================================================================
*/}}

{{- define "institutional-quant.dashboardImage" -}}

{{ printf "%s/%s:%s" .Values.global.imageRegistry .Values.images.dashboard.repository .Values.images.dashboard.tag }}

{{- end }}

{{/*
==============================================================================
Service Account
==============================================================================
*/}}

{{- define "institutional-quant.serviceAccountName" -}}

{{ include "institutional-quant.fullname" . }}

{{- end }}

{{/*
==============================================================================
API Name
==============================================================================
*/}}

{{- define "institutional-quant.apiName" -}}

{{ include "institutional-quant.fullname" . }}-api

{{- end }}

{{/*
==============================================================================
Analytics Name
==============================================================================
*/}}

{{- define "institutional-quant.analyticsName" -}}

{{ include "institutional-quant.fullname" . }}-analytics

{{- end }}

{{/*
==============================================================================
Dashboard Name
==============================================================================
*/}}

{{- define "institutional-quant.dashboardName" -}}

{{ include "institutional-quant.fullname" . }}-dashboard

{{- end }}

{{/*
==============================================================================
Ingress Host
==============================================================================
*/}}

{{- define "institutional-quant.hostname" -}}

{{ .Values.ingress.hostname }}

{{- end }}

{{/*
==============================================================================
TLS Secret
==============================================================================
*/}}

{{- define "institutional-quant.tlsSecret" -}}

{{ .Values.ingress.tls.secretName }}

{{- end }}

{{/*
==============================================================================
Storage Class
==============================================================================
*/}}

{{- define "institutional-quant.storageClass" -}}

{{ .Values.persistence.storageClass }}

{{- end }}

{{/*
==============================================================================
Image Pull Policy
==============================================================================
*/}}

{{- define "institutional-quant.pullPolicy" -}}

{{ .Values.global.imagePullPolicy }}

{{- end }}

{{/*
==============================================================================
Environment
==============================================================================
*/}}

{{- define "institutional-quant.environment" -}}

{{ .Values.global.environment }}

{{- end }}