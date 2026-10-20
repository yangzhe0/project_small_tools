"""Verify source semantics, accounting, shared plot inputs and final PNGs.

A successful run verifies these checks, not unresolved scientific definitions.
"""
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
import csv
import hashlib
import json
import math
import tempfile
import unittest
from PIL import Image
from paths import ROOT, DATA, FIGURES, CACHE
from imcce_pipeline import POLICY,CATEGORIES,build,read_sources,load_stations,parse_station,space_source,geodetic_latitude


def read_csv(name):
    with (DATA/name).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))


class SourceAndArtifactChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources={s['file_id']:s for s in read_sources()}
        cls.stations=load_stations()
        cls.ledger={r['file_id']:r for r in read_csv('catalogue_source_ledger.csv')}
        cls.records=read_csv('record_classification.csv')
        cls.stats=read_csv('satellite_statistics.csv')
        cls.station_rows=read_csv('observatory_satellite_summary.csv')

    def test_fixed_columns_preserve_spaces_and_pad_numeric_codes(self):
        for fid in ['sm0034','sm0035','sm0036']:
            source=self.sources[fid]
            for _,line in source['lines']:
                expected=line[27:30].strip().zfill(3)
                self.assertEqual(parse_station(source,line)[0],expected)
        self.assertEqual(parse_station(self.sources['sm0036'],self.sources['sm0036']['lines'][0][1])[0],'787')
        source=self.sources['sm0036']
        self.assertEqual(sum(parse_station(source,l)[0]=='786' for _,l in source['lines']),9403)

    def test_published_mixed_station_fields(self):
        expected={'jo0078':{'286':631,'O44':199,'O49':81},'so0039':{'327':667,'337':506},'nm0019':{'327':139,'337':956},'jo0080':{'286':2138,'O44':216}}
        for fid,counts in expected.items():
            got=Counter(parse_station(self.sources[fid],l)[0] for _,l in self.sources[fid]['lines'])
            self.assertEqual(dict(got),counts)

    def test_no_arbitrary_token_station_inference(self):
        s=self.sources['jo0066']
        self.assertIsNone(s['meta']['station_field'])
        for _,line in s['lines']:self.assertIsNone(parse_station(s,line)[0])

    def test_space_missions_and_ground_wise(self):
        for fid in ['jo0069','jo0077','sm0085','so0051','um0136','nm0087','nm1034','um0047','sm0076']:
            self.assertTrue(space_source(self.sources[fid]),fid)
            self.assertEqual(int(self.ledger[fid]['mapped_count']),0,fid)
        fake=dict(meta=dict(site='097 - Wise Observatory'),site_raw='097 - Wise Observatory')
        self.assertFalse(space_source(fake))

    def test_station_identities_and_coordinates(self):
        s=self.stations
        self.assertIn('Yaoan',s['O49']['name']);self.assertTrue(100<s['O49']['longitude']<102)
        self.assertTrue(25<s['O49']['latitude']<26)
        for code,country in [('M22','South Africa'),('W68','Chile'),('I41','USA'),('T05','USA'),('T08','USA')]:self.assertEqual(s[code]['country'],country)
        self.assertLess(s['T08']['longitude'],-155);self.assertLess(s['M22']['latitude'],0)
        self.assertLess(s['W84']['latitude'],0);self.assertIsNone(s['248']['latitude'])
        # Independent forward ellipsoid check at several heights, including a mountain site.
        a=6378137;f=1/298.257223563;e2=f*(2-f)
        for deg,h in [(25,2000),(-30,1500),(45,0),(0,100),(80,500)]:
            phi=math.radians(deg);n=a/math.sqrt(1-e2*math.sin(phi)**2)
            c=(n+h)*math.cos(phi)/a;z=(n*(1-e2)+h)*math.sin(phi)/a
            self.assertAlmostEqual(geodetic_latitude(c,z),deg,places=7)

    def test_each_input_has_one_accounting_destination(self):
        classified=defaultdict(Counter)
        for row in self.records:classified[row['file_id']][row['status']]+=int(row['count'])
        for fid,r in self.ledger.items():
            c=classified[fid]
            self.assertEqual(sum(c.values()),int(r['input_count']),fid)
            for status in ['mapped','space','unresolved','excluded']:self.assertEqual(c[status],int(r[status+'_count']),fid)
            self.assertEqual(int(r['residual']),0)
        for r in self.stats:
            self.assertEqual(int(r['raw_input_entries']),sum(int(r[k]) for k in ['mapped_entries','space_entries','unresolved_entries','excluded_entries']))

    def test_exclusions_and_author_boundary(self):
        for fid in POLICY['full_exclusions']:self.assertEqual(int(self.ledger[fid]['selected_count']),0)
        self.assertEqual(self.ledger['jo0078']['team'],'False')
        self.assertEqual(self.ledger['nm0091']['team'],'True')
        self.assertIn('2024',self.ledger['supplement_zhang2024']['reference'])
        self.assertFalse(any(r['file_id']=='nm0090' and r['status']=='mapped' for r in self.records))
        for rule in POLICY['exact_epoch_replacements']:
            newer=self.sources[rule['new']]['lines']
            def key(line):
                t=line.split()
                return (int(t[0]),int(t[1]),Decimal(t[2])) if rule['schema']=='ymd_station' else (Decimal(t[0]),int(t[1]))
            newkeys={key(l) for _,l in newer}
            expected={n for n,l in self.sources[rule['old']]['lines'] if key(l) in newkeys}
            actual={int(r['line']) for r in self.records if r['file_id']==rule['old'] and r['status']=='excluded'}
            self.assertEqual(actual,expected)

    def test_partial_unknowns_not_redistributed(self):
        # Every parsed nonaggregate output preserves one raw row's declared weight.
        for r in self.records:
            if int(r['line']) and r['status']!='excluded':self.assertIn(int(r['count']),[1,2])
        unknown=[r for r in self.records if r['file_id']=='jo0066']
        self.assertTrue(unknown);self.assertTrue(all(r['status']=='unresolved' for r in unknown))
        self.assertTrue(any(r['status']=='unresolved' and int(r['count'])>0 for r in self.records))

    def test_country_station_and_plot_reconciliation(self):
        c=defaultdict(Counter)
        for r in self.station_rows:
            self.assertEqual(sum(int(r[k]) for k in CATEGORIES),int(r['total_obs']))
            self.assertIsNotNone(self.stations[r['code']]['latitude'])
            for k in CATEGORIES+['total_obs']:c[r['country']][k]+=int(r[k])
        for r in read_csv('country_satellite_summary.csv'):
            for k in CATEGORIES+['total_obs']:self.assertEqual(c[r['country']][k],int(r[k]))
        bars=json.loads((DATA/'barchart_metadata.json').read_text(encoding='utf-8'))
        selected=next(r for r in bars if r['mode']=='selected')
        self.assertEqual(selected['team'],[int(r['selected_team_entries']) for r in self.stats])
        self.assertEqual(selected['global_entries'],[int(r['selected_entries']) for r in self.stats])
        maps=json.loads((DATA/'map_metadata.json').read_text(encoding='utf-8'))
        self.assertEqual(maps['input_sha256'],hashlib.sha256((DATA/'observatory_satellite_summary.csv').read_bytes()).hexdigest())
        self.assertEqual(maps['layout'],'approved_A_map_first')
        from generate_all_satellite_maps import CONFIG
        self.assertEqual([(m['key'],m['title']) for m in maps['maps']],[(key,title) for key,title,_ in CONFIG])
        for m in maps['maps']:
            self.assertEqual(m['selected_entries'],m['mapped_entries']+m['space_entries']+m['unresolved_entries'])
            self.assertEqual(m['china_entries'],sum(int(r[m['key']]) for r in self.station_rows if r['country']=='China'))
            self.assertEqual(m['text_collisions'],[])
            self.assertEqual(m['obscured_world_sites'],[])
            if m['key']!='total_obs':self.assertEqual(m['mapped_entries'],sum(int(r[m['key']]) for r in self.station_rows))

    def test_current_png_sizes_and_shared_counts(self):
        from generate_all_satellite_maps import CONFIG
        files=['number.png']+[r[2] for r in CONFIG]
        for name in files:
            with Image.open(FIGURES/name) as im:
                self.assertEqual(im.height,2350,name)
                self.assertEqual(im.width,3420 if name=='number.png' else 4804,name)
                im.verify()
        bars=json.loads((DATA/'barchart_metadata.json').read_text(encoding='utf-8'))[0]
        self.assertEqual(bars['team'],[int(r['selected_team_entries']) for r in self.stats])
        self.assertEqual(bars['global_entries'],[int(r['selected_entries']) for r in self.stats])

    def test_rebuild_is_deterministic(self):
        cache=CACHE;cache.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache,prefix='verify-') as tmp:
            build(tmp)
            for name in ['satellite_statistics.csv','catalogue_source_ledger.csv','record_classification.csv','observatory_satellite_summary.csv','country_satellite_summary.csv','unresolved_records_flagged.csv','excluded_records.csv','raw_records_outside_catalogue_scope.csv','pipeline_manifest.json']:
                self.assertEqual((DATA/name).read_bytes(),(Path(tmp)/name).read_bytes(),name)


if __name__=='__main__':
    unittest.main(verbosity=2)
