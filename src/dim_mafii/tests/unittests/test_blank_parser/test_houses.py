from typing import List

from expects import expect, have_len, equal
from dim_mafii.domain.events import CreateOrUpdateHouse
from dim_mafii.domain.types import ClassicRole
from dim_mafii.sheet_parser.blank_version_2 import BlankParser
from dim_mafii.tests.unittests.test_blank_parser.common import BlankParserMixin


class WhenHousesAreParsed(BlankParserMixin):

    def given_blank_parser(self):
        matrix = self.get_matrix_data('ПеремогаМирних')
        self.blank_parser = BlankParser(matrix)

    def because_we_parse_game_info(self):
        self.houses_events: List[CreateOrUpdateHouse] = self.blank_parser.parse_houses()

    def it_should_parse_ten_houses(self):
        expect(self.houses_events).to(have_len(10))

    def it_should_correctly_parse_house_on_slot_1(self):
        house = self.houses_events[0]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('монист'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(1))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(1))

    def it_should_correctly_parse_house_on_slot_2(self):
        house = self.houses_events[1]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('інкогніто'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(2))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_3(self):
        house = self.houses_events[2]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('боровик'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(3))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(3))

    def it_should_correctly_parse_house_on_slot_4(self):
        house = self.houses_events[3]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('скарлет'))
        expect(house.role).to(equal(ClassicRole.mafia))
        expect(house.slot).to(equal(4))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(1))

    def it_should_correctly_parse_house_on_slot_5(self):
        house = self.houses_events[4]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('абракадабра'))
        expect(house.role).to(equal(ClassicRole.mafia))
        expect(house.slot).to(equal(5))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_6(self):
        house = self.houses_events[5]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('соліс'))
        expect(house.role).to(equal(ClassicRole.sheriff))
        expect(house.slot).to(equal(6))
        expect(house.bonus_mark).to(equal(0.3))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_7(self):
        house = self.houses_events[6]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('кара'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(7))
        expect(house.bonus_mark).to(equal(0.2))
        expect(house.fouls).to(equal(0))

    def it_should_correctly_parse_house_on_slot_8(self):
        house = self.houses_events[7]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('ната'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(8))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_9(self):
        house = self.houses_events[8]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('еморі'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(9))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(0))

    def it_should_correctly_parse_house_on_slot_10(self):
        house = self.houses_events[9]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('нещадний'))
        expect(house.role).to(equal(ClassicRole.don))
        expect(house.slot).to(equal(10))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))
