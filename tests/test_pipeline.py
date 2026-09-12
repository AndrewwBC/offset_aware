import unittest
from run_experiment import token_map,split_sentences,few_shot_messages
from run_ablation_direct_v3 import raw_prompt,normalize_raw
class PipelineTests(unittest.TestCase):
 def test_attached_punctuation_and_unicode(self):
  text='O sofá é bom.\nOutro texto.'
  units=split_sentences(text);self.assertEqual(units[0],('O sofá é bom.',0,13));self.assertEqual(text[units[1][1]:units[1][2]],'Outro texto.')
  self.assertEqual(token_map('competente.Tem')[0]['token'],'competente.Tem')
 def test_direct_prompts(self):
  for task in ['ssa','asqp']:
   self.assertNotIn('token_ids',raw_prompt(task))
   self.assertNotIn('token_ids',str(few_shot_messages(task,False)))
 def test_mismatch_rejected(self):
  row={'category':'general','polarity':'POS','aspect':{'term':'hotel','location':[2,7]},'sentiment':{'term':'bom','location':[8,11],'type':'explicit'}}
  out,errors=normalize_raw({'annotations':[row]},'O hotel bom',10,'asqp',True)
  self.assertFalse(errors);self.assertEqual(out[0]['aspect']['location'],[12,17])
  row['sentiment']['term']='ruim';out,errors=normalize_raw({'annotations':[row]},'O hotel bom',10,'asqp',True)
  self.assertTrue(errors);self.assertEqual(out,[])
if __name__=='__main__':unittest.main()
