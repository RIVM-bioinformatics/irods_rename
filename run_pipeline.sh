#!/bin/bash
set -x

#----------------------------------------------#
# User parameters
input_dir="${1%/}"
output_dir="${2%/}"
PROJECT_NAME="${irods_input_projectID}" # This should be an environment variable

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null 2>&1 && pwd )"
cd ${DIR}

# Sanity checks
if [ ! -z "${1}" ] || [ ! -z "${2}" ] || [ ! -z "${irods_input_projectID}" ]
then
  INPUTDIR="${1}"
  OUTPUTDIR="${2}"
  PROJECT_NAME="${irods_input_projectID}"
else
  echo "No inputdir, outputdir or project name (param 1, 2, irods_input_projectID)"
  exit 1
fi

#check if there is an rename file, otherwise exit
if [ ! -z "${irods_input_sequencing__run_id}" ] && [ -f "/data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.rename" ]
then
  RENAME_FILE="/data/BioGrid/NGSlab/sample_sheets/${irods_input_sequencing__run_id}.rename"
else
  # exit here if the rename file does not exist
fi

if [ ! -d "${INPUTDIR}" ] || [ ! -d "${OUTPUTDIR}" ]
then
  echo "inputdir $INPUTDIR or output dir $OUTPUTDIR does not exist!"
  exit 1
fi

set -euo pipefail

echo -e "\nRun pipeline..."

python rename.py ${INPUTDIR} ${OUTPUTDIR} ${RENAME_FILE}

result=$?

# Propagate metadata

set +euo pipefail

SEQ_KEYS=
SEQ_ENV=`env | grep irods_input_sequencing`
for SEQ_AVU in ${SEQ_ENV}
do
    SEQ_KEYS="${SEQ_KEYS} ${SEQ_AVU%%=*}"
done

for key in $SEQ_KEYS irods_input_illumina__Flowcell \
    irods_input_illumina__Instrument \
    irods_input_illumina__Date \
    irods_input_illumina__Run_number \
    irods_input_illumina__Run_Id \
    irods_input_minion__flow_cell_id \
    irods_input_minion__sample_id \
    irods_input_user__runinfo__name \
    irods_input_user__runinfo__id
do
    if [ ! -z ${!key} ] ; then
        attrname=${key:12}
        attrname=${attrname/__/::}
        echo "${attrname}: '${!key}'" >> ${OUTPUTDIR}/metadata.yml
    fi
done

exit ${result}