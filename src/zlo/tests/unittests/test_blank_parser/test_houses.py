from typing import List

from expects import expect, have_len, equal
from zlo.domain.events import CreateOrUpdateHouse
from zlo.domain.types import ClassicRole
from zlo.sheet_parser.blank_version_2 import BlankParser
from zlo.tests.unittests.test_blank_parser.common import BlankParserMixin


class When_houses_are_parsed(BlankParserMixin):

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
        expect(house.player_nickname).to(equal('Монист'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(1))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(1))

    def it_should_correctly_parse_house_on_slot_2(self):
        house = self.houses_events[1]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Інкогніто'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(2))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_3(self):
        house = self.houses_events[2]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Боровик'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(3))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(3))

    def it_should_correctly_parse_house_on_slot_4(self):
        house = self.houses_events[3]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Скарлет'))
        expect(house.role).to(equal(ClassicRole.mafia))
        expect(house.slot).to(equal(4))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(1))

    def it_should_correctly_parse_house_on_slot_5(self):
        house = self.houses_events[4]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Абракадабра'))
        expect(house.role).to(equal(ClassicRole.mafia))
        expect(house.slot).to(equal(5))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_6(self):
        house = self.houses_events[5]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Соліс'))
        expect(house.role).to(equal(ClassicRole.sheriff))
        expect(house.slot).to(equal(6))
        expect(house.bonus_mark).to(equal(0.3))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_7(self):
        house = self.houses_events[6]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Кара'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(7))
        expect(house.bonus_mark).to(equal(0.2))
        expect(house.fouls).to(equal(0))

    def it_should_correctly_parse_house_on_slot_8(self):
        house = self.houses_events[7]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Ната'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(8))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))

    def it_should_correctly_parse_house_on_slot_9(self):
        house = self.houses_events[8]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Еморі'))
        expect(house.role).to(equal(ClassicRole.citizen))
        expect(house.slot).to(equal(9))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(0))

    def it_should_correctly_parse_house_on_slot_10(self):
        house = self.houses_events[9]
        expect(house.game_id).to(equal('2440a5c9-01ce-4d07-b8a4-59559179a2b1'))
        expect(house.player_nickname).to(equal('Нещадний'))
        expect(house.role).to(equal(ClassicRole.don))
        expect(house.slot).to(equal(10))
        expect(house.bonus_mark).to(equal(0))
        expect(house.fouls).to(equal(2))
