from troposphere import Ref, Template
from troposphere.ec2 import Tag, SecurityGroup, SecurityGroupIngress, SecurityGroupEgress


class Stack(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data

        self.create_security_groups()

    def create_security_groups(self):
        t = self.template

        groups = self.sceptre_user_data['groups']

        for group in groups:
            group_name = group['group_name']
            group_desc = group['group_desc']

            self.group_name = t.add_resource(SecurityGroup(
                group_name,
                VpcId=self.sceptre_user_data['vpc_id'],
                GroupDescription=group_desc,
                Tags=[Tag('Name', group_name)]
                ))

            if 'ingress_rules' in group:
                self.create_rules(t, group['ingress_rules'], self.group_name, 'ingress')
            elif 'egress_rules' in group:
                self.create_rules(t, group['egress_rules'], self.group_name, 'egress')

    def create_rules(self, template, rules, sg, rule_type):
        for rule in rules:
            if rule_type is 'ingress':
                self.add_ingress_rule(template, rule, sg)
            elif rule_type is 'egress':
                self.add_egress_rule(template, rule, sg)

    def add_ingress_rule(self, template, rule, sg):
        if 'sg' in rule:
             template.add_resource(
                SecurityGroupIngress(
                    rule['name'],
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol='tcp',
                    GroupId=Ref(sg),
                    Description=rule['description'],
                    SourceSecurityGroupId=Ref(rule['sg'])
                    )
                )
        elif 'cidr_ip' in rule:
             template.add_resource(
                SecurityGroupIngress(
                    rule['name'],
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol='tcp',
                    CidrIp=rule['cidr_ip'],
                    GroupId=Ref(sg),
                    Description=rule['description']
                    )
                )

    def add_egress_rule(self, template, rule, sg):
        if 'sg' in rule:
            template.add_resource(
                SecurityGroupEgress(
                    rule['name'],
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol='tcp',
                    GroupId=Ref(sg),
                    Description=rule['description'],
                    DestinationSecurityGroupId=Ref(rule['sg'])
                    )
                )
        elif 'cidr_ip' in rule:
            template.add_resource(
                SecurityGroupEgress(
                    rule['name'],
                    ToPort=rule['to_port'],
                    FromPort=rule['from_port'],
                    IpProtocol='tcp',
                    CidrIp=rule['cidr_ip'],
                    GroupId=Ref(sg),
                    Description=rule['description']
                    )
                )


def sceptre_handler(sceptre_user_data):
    stack = Stack(sceptre_user_data)
    return stack.template.to_json()
