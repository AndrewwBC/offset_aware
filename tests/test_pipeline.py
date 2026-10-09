import unittest
from run_experiment import token_map,split_sentences,few_shot_messages
from run_ablation_direct_v3 import raw_prompt,normalize_raw
class PipelineTests(unittest.TestCase):
 def test_word_tokens_and_unicode(self):
  text='O sofá é bom.\nOutro texto.'
  units=split_sentences(text);self.assertEqual(units[0],('O sofá é bom.',0,13));self.assertEqual(text[units[1][1]:units[1][2]],'Outro texto.')
  toks=token_map('competente.Tem wi-fi, R$ 50!')
  self.assertEqual([t['token'] for t in toks],['competente','Tem','wi','fi','R','50'])
  s='competente.Tem wi-fi, R$ 50!';self.assertEqual(s[toks[2]['start']:toks[3]['end']],'wi-fi');self.assertEqual(s[toks[4]['start']:toks[5]['end']],'R$ 50')
 def test_few_shot_terms(self):
  terms=[(a['aspect']['term'],a['sentiment']['term']) for m in few_shot_messages(True) if m['role']=='assistant' for a in __import__('json').loads(m['content'])['annotations']]
  self.assertEqual(terms,[('hotel','excelente'),('quarto','pequeno'),('localizacao','otima'),('preco','alto'),('atendimento','impecavel')])
 def test_direct_prompts(self):
  self.assertNotIn('token_ids',raw_prompt())
  self.assertNotIn('token_ids',str(few_shot_messages(False)))
 def test_mismatch_rejected(self):
  row={'category':'general','polarity':'POS','aspect':{'term':'hotel','location':[2,7]},'sentiment':{'term':'bom','location':[8,11],'type':'explicit'}}
  out,errors=normalize_raw({'annotations':[row]},'O hotel bom',10,True)
  self.assertFalse(errors);self.assertEqual(out[0]['aspect']['location'],[12,17])
  row['sentiment']['term']='ruim';out,errors=normalize_raw({'annotations':[row]},'O hotel bom',10,True)
  self.assertTrue(errors);self.assertEqual(out,[])
if __name__=='__main__':unittest.main()
