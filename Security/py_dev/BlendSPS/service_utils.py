import time
import logging
import os
import copy

from utilities import TypesUtil, FileUtil
from wrapper_pyca import Crypto_Hash, Crypto_DSA
from Tender_RPC import Tender_RPC


logger = logging.getLogger(__name__)
# indextoken_logger = logging.getLogger("Index_Token")
# indextoken_logger.setLevel(logging.INFO)


class TenderUtils(object):
    @staticmethod
    def load_ENF(ENF_file):
        '''
        Load ENF data from ENF_file

        Args:
            ENF_name: ENF file name
        Returns:
            json_ENF: json format ENF data

        '''
        ls_lines=FileUtil.ReadLines(ENF_file)
        ls_record=[]
        for line in ls_lines:
            #print(line[:-1].split(';'))
            ls_record.append(line[:-1].split(';'))

        ls_ENF=[]
        for record in ls_record:
            ls_ENF.append( format(float(record[0]), '.2f') )

        # print(ls_ENF)
        json_ENF = {}
        json_ENF['id']=ENF_file
        json_ENF['ENF']=ls_ENF

        return json_ENF


    @staticmethod
    def verify_ENF(ENF_file):
        '''
        Verify ENF value by querying from blockchain

        Args:
            ENF_name: ENF file name
        Returns:
            Verified result: True or False
        '''
        # 1) Read token data using call
        ls_time_exec = []

        query_json = {}
        query_json['data']='"' + ENF_file +'"'
        start_time=time.time()

        query_ret=Tender_RPC.abci_query(query_json)

        # -------- parse value from response and display it ------------
        key_str=query_ret['result']['response']['key']
        value_str=query_ret['result']['response']['value']
        logger.info("Fetched ENF value:")
        logger.info("id: {}".format(TypesUtil.base64_to_ascii(key_str)) )
        if( value_str!= None):
            query_ENF_value = TypesUtil.base64_to_ascii(value_str)
        else:
            query_ENF_value = ''
        # convert tx to json format
        query_ENF_json = TypesUtil.tx_to_json(query_ENF_value)
        logger.info("value: {}".format(query_ENF_json))

        # 2) verify signature
        string_ENF = str(query_ENF_json['ENF'])
        byte_ENF = TypesUtil.string_to_bytes(string_ENF)
        sign_ENF = TypesUtil.hex_to_string(query_ENF_json['sign_ENF'])

        load_public_key_bytes = Crypto_DSA.load_key_bytes('public_key_file')
        reload_public_key = Crypto_DSA.load_public_key_bytes(load_public_key_bytes)
        verify_sign=Crypto_DSA.verify(reload_public_key,sign_ENF,byte_ENF)
        logger.info("Sign verification: {}".format(verify_sign))
        
        exec_time=time.time()-start_time
        ls_time_exec.append( format( exec_time*1000, '.3f' ) ) 

        # Prepare log messgae
        str_time_exec=" ".join(ls_time_exec)
        FileUtil.save_testlog('test_results', 'exec_verify_ENF.log', str_time_exec)

        # 3) return verify hash model result
        return verify_sign

    @staticmethod
    def tx_evaluate(ENF_file):
        '''
        Launch tx and evaluate tx committed time

        Args:
            ENF_file: ENF file name
        Returns:
            tx committed reulst
        '''
        # 1) load ENF data from file
        json_ENF = TenderUtils.load_ENF(ENF_file)
        logger.info(json_ENF)

        # 2) sign ENF data in json_ENF['ENF']
        string_ENF = str(json_ENF['ENF'])
        byte_ENF = TypesUtil.string_to_bytes(string_ENF)
        load_private_key_bytes = Crypto_DSA.load_key_bytes('private_key_file')
        reload_private_key = Crypto_DSA.load_private_key_bytes(load_private_key_bytes, 
                                                                encryp_pw=b'samuelxu999')
        sign_ENF = Crypto_DSA.sign(reload_private_key, byte_ENF)
        logger.info(sign_ENF)

        # 3) evaluate tx committed time
        start_time=time.time()
        logger.info("tx signed ENF: {} to blockchain...\n".format(ENF_file)) 

        # -------- prepare parameter for tx ------------
        tx_json = {}
        key_str = ENF_file
        value_json = {}
        value_json['ENF']=json_ENF['ENF']
        value_json['sign_ENF']=TypesUtil.string_to_hex(sign_ENF)
        # convert json to tx format
        value_str = TypesUtil.json_to_tx(value_json)
        tx_data = key_str + "=" + value_str 
        # --------- build parameter string: tx=? --------
        tx_json['tx']='"' + tx_data +'"' 
        # print(tx_json)
        tx_ret=Tender_RPC.broadcast_tx_commit(tx_json)
        exec_time=time.time()-start_time
        logger.info("tx committed time: {:.3f}\n".format(exec_time, '.3f')) 
        FileUtil.save_testlog('test_results', 'exec_tx_commit_ENF.log', format(exec_time, '.3f'))
        # print(tx_ret)
        return tx_ret
